from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import connection
from django.db.utils import OperationalError
import mysql.connector
import os
from django.conf import settings
from .models import QueryRecord
from decimal import Decimal
import plotly.graph_objects as go
import base64
from io import BytesIO


# ChatGLM
from dashscope import Generation
import dashscope
dashscope.api_key="********************"

# Zhipu
from zhipuai import ZhipuAI

# Spark
from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage
SPARKAI_URL = 'wss://spark-api.xf-yun.com/v3.5/chat'
SPARKAI_APP_ID = '2516f528'
SPARKAI_API_SECRET = '********************'
SPARKAI_API_KEY = '********************'
SPARKAI_DOMAIN = 'generalv3.5'

# Tencent
import json
import types
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.hunyuan.v20230901 import hunyuan_client, models

def get_databases(request):
    """
    获取所有数据库的接口
    """
    cursor = connection.cursor()
    cursor.execute("SHOW DATABASES")
    databases = [row[0] for row in cursor.fetchall()]
    return JsonResponse({'databases': databases})

def get_tables(request, database_name):
    """
    获取某个数据库的所有表名的接口
    """
    cursor = connection.cursor()
    cursor.execute(f"USE {database_name}")
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    return JsonResponse({'tables': tables})

def get_table_data(request, database_name, table_name):
    """
    获取某个表的所有数据的接口
    """
    cursor = connection.cursor()
    cursor.execute(f"USE {database_name}")
    cursor.execute(f"SELECT * FROM {table_name}")
    columns = [col[0] for col in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return JsonResponse({'columns': columns, 'rows': rows})


# 读取上传的 SQL 文件并执行
def read_sql_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        sql_script = file.read()
    return sql_script

# 执行建库的SQL
def create_database(host, user, password, database, sql_script):
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
        cursor.execute(f"USE {database}")
        for result in cursor.execute(sql_script, multi=True):
            if result.with_rows:
                result.fetchall()
        conn.commit()
        conn.close()
        print("数据库创建成功！")
    except mysql.connector.Error as e:
        print("数据库创建失败：", e)

@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            return JsonResponse({'message': 'No file provided'}, status=400)

        uploaded_file = request.FILES['file']
        uploads_dir = os.path.join(settings.BASE_DIR, 'myapp', 'uploads')

        # 创建 uploads 目录
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)

        file_path = os.path.join(uploads_dir, uploaded_file.name)

        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        sql_script = read_sql_file(file_path)

        try:
            host = '127.0.0.1'
            user = 'root'
            password = 'root123a'
            database = request.POST.get('database_name', 'default_database_name')
            print("Database Name:", database)
            create_database(host, user, password, database, sql_script)

            message = f'文件 {uploaded_file.name} 上传成功！'
            return JsonResponse({'message': message, 'db_created': True, 'db_message': '数据库创建成功！'})
        except mysql.connector.Error as e:
            return JsonResponse({'message': f'文件上传成功，但是数据库创建失败：{e}', 'db_created': False, 'db_message': '数据库创建失败'}, status=500)




# 获取数据库的基本信息
def get_database_info(database):
    database_info = []
    with connection.cursor() as cursor:
        cursor.execute(f"USE `{database}`")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        for table in tables:
            table_name = table[0]
            table_dict = {"table_name": table_name, "columns": []}
            cursor.execute(f"SHOW FULL COLUMNS FROM `{table_name}`")
            columns_info = cursor.fetchall()
            for column_info in columns_info:
                column_name = column_info[0]
                data_type = column_info[1]
                is_primary_key = "PRI" in column_info[4]
                column_dict = {
                    "column_name": column_name,
                    "data_type": data_type,
                    "is_primary_key": is_primary_key
                }
                table_dict["columns"].append(column_dict)
            database_info.append(table_dict)
    return database_info

# 数据库信息转换为string，便于传输
def database_info_to_string(database_info):
    info_string = ""
    for table_info in database_info:
        table_name = table_info['table_name']
        column_names = ", ".join([column['column_name'] for column in table_info['columns']])
        info_string += f"Table: {table_name}\nColumns: {column_names}\n\n"
    return info_string

def call_with_messages_ChatGLM(info_string, user_query):
    messages = [
        {'role': 'system', 'content': 'You are a clever system.'},
        {'role': 'user', 'content': '现在，我有一个问题：{}。请将上面的自然语言查询转换为SQL语句。表结构：{}。另外，查询应严格以纯文本的SQL语句形式返回，而不是以JSON形式返回。返回正确符合语法的SQL。只要SQL。'.format(user_query, info_string)}
    ]
    gen = Generation()
    response = gen.call(
        'chatglm3-6b',
        messages=messages,
        result_format='message',
    )
    sql_query = response['output']['choices'][0]['message']['content']
    sql_query = sql_query.replace('\n', ' ')
    return sql_query


def call_with_messages_Zhipu(info_string, user_query):
    client = ZhipuAI(api_key="********************")
    response = client.chat.completions.create(
        model="glm-4",
        messages=[
            {"role": "user", "content": f"表结构: {info_string}\n\n请将以下自然语言查询转换为SQL语句，只返回SQL语句本身，不需要其他解释。不要任何的注意！！！！：{user_query}"}
        ],
    )
    sql_query = response.choices[0].message.content.strip()
    # 提取实际的SQL查询语句
    sql_query_lines = sql_query.split('\n')
    complete_sql_query = []
    select_found = False
    for line in sql_query_lines:
        line = line.strip()
        if line.lower().startswith("select"):
            select_found = True
        if select_found:
            complete_sql_query.append(line)
        if line.endswith(';'):
            break
    if select_found:
        sql_query = " ".join(complete_sql_query)
        return sql_query
    else:
        print("Invalid SQL query generated.")


def call_with_messages_Spark(info_string, user_query):
    spark = ChatSparkLLM(
        spark_api_url=SPARKAI_URL,
        spark_app_id=SPARKAI_APP_ID,
        spark_api_key=SPARKAI_API_KEY,
        spark_api_secret=SPARKAI_API_SECRET,
        spark_llm_domain=SPARKAI_DOMAIN,
        streaming=False,
    )
    prompt = '完成Text2SQL 任务，数据库中有以下表{}：,回答以下问题{}。返回纯文本sql'.format(info_string,user_query)
    messages = [ChatMessage(
        role="user",
        content=prompt
    )]
    handler = ChunkPrintHandler()
    response = spark.generate([messages], callbacks=[handler])
    # 检查回复是否以SELECT开头
    if response and response.generations and response.generations[0]:
        generated_text = response.generations[0][0].text
        if generated_text.startswith('SELECT'):
            sql_query=generated_text
            return sql_query
        else:
            print("回答不符合要求:", generated_text)
    else:
        print("未生成有效回复")

def call_with_messages_Tencent(info_string, user_query):
    try:
        cred = credential.Credential("********************", "********************")
        httpProfile = HttpProfile()
        httpProfile.endpoint = "hunyuan.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = hunyuan_client.HunyuanClient(cred, "", clientProfile)
        combined_message = (
            "数据库表结构：{}，\n\n 问题：{} 请根据数据库信息，直接给出该问题的sql查询语句，注意是直接给sql语言".format(info_string,user_query))
        req = models.ChatCompletionsRequest()
        params = {
            "Model": "hunyuan-standard",
            "Messages": [
                {
                    "Role": "user",
                    "Content": combined_message
                }
            ]
        }
        req.from_json_string(json.dumps(params))
        resp = client.ChatCompletions(req)
        if isinstance(resp, types.GeneratorType):  # 流式响应
            for event in resp:
                event_data = json.loads(event)
                content = event_data.get("Response", {}).get("Choices", [{}])[0].get("Message", {}).get("Content", "")
                print(content)
        else:  # 非流式响应
            resp_json = json.loads(resp.to_json_string())
            content = resp_json.get("Choices", [{}])[0].get("Message", {}).get("Content", "")
            print(content)
        sql_query = content
        return sql_query

    except TencentCloudSDKException as err:
        print(f"接口调用失败：{err}")

# 执行产生的SQL语句并返回结果
def execute_query(sql_query, database):
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"USE `{database}`")
            cursor.execute(sql_query)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return columns, results
    except Exception as e:
        print("SQL Execution Error:", e)
        return None, None


@csrf_exempt
def natural_sql(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query')
            database = data.get('database')
            database_info = get_database_info(database)
            info_string = database_info_to_string(database_info)
            print(info_string)
            print(query)
            print("----------ChatGLM3.6-----------")
            sql_query_chatglm = call_with_messages_ChatGLM(info_string, query)
            print(sql_query_chatglm)
            print("----------Zhipu4-----------")
            sql_query_zhipu = call_with_messages_Zhipu(info_string, query)
            print(sql_query_zhipu)
            print("----------Spark-----------")
            sql_query_spark = call_with_messages_Spark(info_string, query)
            print(sql_query_spark)
            print("----------Tencent-----------")
            sql_query_tencent = call_with_messages_Tencent(info_string, query)
            print(sql_query_tencent)

            if sql_query_chatglm:
                chatglm36_columns, chatglm36_results = execute_query(sql_query_chatglm,database)
                print("----------ChatGLM3.6-----------")
                print("ChatGLM Query Results:", chatglm36_results)
            if sql_query_zhipu:
                zhipu4_columns, zhipu4_results = execute_query(sql_query_zhipu,database)
                print("----------Zhipu4-----------")
                print("Zhipu Query Results:", zhipu4_results)
            if sql_query_spark:
                spark_columns, spark_results = execute_query(sql_query_spark,database)
                print("----------Spark-----------")
                print("Spark Query Results:", spark_results)
            if sql_query_spark:
                tencent_columns, tencent_results = execute_query(sql_query_spark,database)
                print("----------Tencent-----------")
                print("Tencent Query Results:", tencent_results)

            response_data = {
                "chatglmColumns": chatglm36_columns,
                "chatglmResults": chatglm36_results,
                "zhipuColumns": zhipu4_columns,
                "zhipuResults": zhipu4_results,
                "sparkColumns": spark_columns,
                "sparkResults": spark_results,
                "tencentColumns": tencent_columns,
                "tencentResults": tencent_results,

            }
            return JsonResponse(response_data, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)

# 保存查询记录
@csrf_exempt
def save_record(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            record = QueryRecord(
                database=data['database'],
                query=data['query'],
                results=data['results'],
            )
            record.save()
            return JsonResponse({"message": "Record saved successfully"}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)

# 展示查询记录
def get_records(request):
    records = QueryRecord.objects.all().order_by('-timestamp')
    records_data = [
        {
            "id": record.id,
            "database": record.database,
            "query": record.query,
            "results": record.results,
            "timestamp": record.timestamp,
        } for record in records
    ]
    return JsonResponse({"records": records_data}, safe=False)

# 限定图的类型
def draw_with_type(columns, results, chart_type):
    num_cols = len(columns)
    xx = [row[columns[0]] for row in results]
    xx = [str(x) for x in xx]
    yy = None
    # 如果执行结果只有两列，x,y轴数据固定为第一，二列
    if num_cols == 2:
        yy = [result[columns[1]] for result in results]
    # 如果执行结果大于两列，x轴数据固定为第一列
    # y轴数据为第一个数据列
    else:
        for i in range(1, num_cols):
            column_data = [result[columns[i]] for result in results]
            if all(isinstance(value, (Decimal, int, float)) for value in column_data):
                yy = column_data
                break
    print(yy)
    fig = go.Figure()
    if chart_type == 'bar':
        fig.add_trace(go.Bar(
            x=xx,
            y=yy,
            orientation='v',
            marker=dict(
                color='skyblue'
            )
        ))
        # 设置布局
        fig.update_layout(
            title='柱形图'
        )
    elif chart_type == 'line':
        fig.add_trace(go.Scatter(
            x=xx,
            y=yy,
            mode='lines+markers',
            line=dict(color='green', width=2),
            marker=dict(color='darkgreen', size=10)
        ))
        # 设置布局
        fig.update_layout(
            title='折线图'
        )
    elif chart_type == 'pie':
        fig.add_trace(go.Pie(
            labels=xx,
            values=yy,
            marker=dict(colors=['gold', 'mediumturquoise', 'darkorange', 'lightgreen']),
        ))
        # 设置布局
        fig.update_layout(
            title='饼图'
        )
    else:
        return "Unsupported chart type"

    fig.show()
    # 将图像保存为Base64编码字符串
    buffer = BytesIO()
    fig.write_image(buffer, format='png',width=500, height=300)
    buffer.seek(0)
    img_str = base64.b64encode(buffer.read()).decode('utf-8')

    return img_str


@csrf_exempt
def visualize(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        chart_type = data.get('chart_type')
        columns = data.get('columns')
        results = data.get('results')
        if chart_type and columns and results:
            image_str = draw_with_type(columns, results, chart_type)
            return JsonResponse({'image_data': image_str})
        else:
            return JsonResponse({'error': 'Missing parameters'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


