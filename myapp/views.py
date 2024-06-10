from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import connection

# ChatGLM
from dashscope import Generation
import dashscope
dashscope.api_key="sk-e6f3dc80013e40d6a085523cf0d4f008"

# Zhipu
from zhipuai import ZhipuAI

'''
# Spark
from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage
SPARKAI_URL = 'wss://spark-api.xf-yun.com/v3.5/chat'
SPARKAI_APP_ID = '2516f528'
SPARKAI_API_SECRET = 'YmQ3MmQ3NDk3YzkxODZlZDQ2MzI5OGJm'
SPARKAI_API_KEY = '67840867de7fb02b7f2e2f082dcaa16c'
SPARKAI_DOMAIN = 'generalv3.5'
'''

# 获取数据库的基本信息
def get_database_info():
    database_info = []
    with connection.cursor() as cursor:
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
    client = ZhipuAI(api_key="8aa7b504acbe1be362f61c5d437f7eba.t9DHRN0whCjbQQ7p")
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

'''
def call_with_messages_Spark(info_string, user_query):
    spark = ChatSparkLLM(
        spark_api_url=SPARKAI_URL,
        spark_app_id=SPARKAI_APP_ID,
        spark_api_key=SPARKAI_API_KEY,
        spark_api_secret=SPARKAI_API_SECRET,
        spark_llm_domain=SPARKAI_DOMAIN,
        streaming=False,
    )
    prompt = '完成Text2SQL 任务，数据库中有以下表{}：,回答以下问题{}'.format(info_string,user_query)
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
            print("回答符合要求:", generated_text)
            sql_query=generated_text
            return sql_query
        else:
            print("回答不符合要求:", generated_text)
    else:
        print("未生成有效回复")
'''



def execute_query(sql_query):
    try:
        with connection.cursor() as cursor:
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
            database_info = get_database_info()
            info_string = database_info_to_string(database_info)
            print(info_string)
            print(query)
            print("----------ChatGLM3.6-----------")
            sql_query_chatglm = call_with_messages_ChatGLM(info_string, query)
            print(sql_query_chatglm)
            print("----------Zhipu4-----------")
            sql_query_zhipu = call_with_messages_Zhipu(info_string, query)
            print(sql_query_zhipu)
            '''
            print("----------Spark-----------")
            sql_query_spark = call_with_messages_Spark(info_string, query)
            print(sql_query_spark)
            '''
            if sql_query_chatglm:
                chatglm36_columns, chatglm36_results = execute_query(sql_query_chatglm)
                print("----------ChatGLM3.6-----------")
                print("ChatGLM Query Results:", chatglm36_results)
            if sql_query_zhipu:
                zhipu4_columns, zhipu4_results = execute_query(sql_query_zhipu)
                print("----------Zhipu4-----------")
                print("Zhipu Query Results:", zhipu4_results)
            '''
            if sql_query_spark:
                spark_columns, spark_results = execute_query(sql_query_spark)
                print("----------Zhipu4-----------")
                print("Spark Query Results:", spark_results)
            '''
            response_data = {
                "chatglmColumns": chatglm36_columns,
                "chatglmResults": chatglm36_results,
                "zhipuColumns": zhipu4_columns,
                "zhipuResults": zhipu4_results,

            }
            return JsonResponse(response_data, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)