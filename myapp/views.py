from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import connection

# ChatGLM
from http import HTTPStatus
from dashscope import Generation
import dashscope
import pymysql
from termcolor import colored
dashscope.api_key="sk-e6f3dc80013e40d6a085523cf0d4f008"

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

def call_with_messages(info_string, user_query):
    messages = [
        {'role': 'system', 'content': 'You are a clever system.'},
        {'role': 'user', 'content': '现在，我有一个问题：{}。我需要请根据以下数据库模式编写SQL查询：{}。另外，查询应严格以纯文本的SQL语句形式返回，而不是以JSON形式返回。返回正确符合语法的SQL。不需要多余的分号。'.format(user_query, info_string)}
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
            sql_query = call_with_messages(info_string, query)
            print(sql_query)

            if sql_query:
                with connection.cursor() as cursor:
                    try:
                        cursor.execute(sql_query)
                        columns = [col[0] for col in cursor.description]
                        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                        print("Query Results:", results)
                        return JsonResponse({"columns": columns, "results": results}, safe=False)
                    except Exception as e:
                        print("SQL Execution Error:", e)
                        return JsonResponse({"error": "SQL execution error: " + str(e)}, status=400)
            else:
                return JsonResponse({"error": "Invalid query"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)