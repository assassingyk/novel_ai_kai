import asyncio
import random
import json

from hoshino import aiorequests


def save_config(config: dict, path):
    try:
        with open(path, 'w', encoding='utf8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as ex:
        print(ex)
        return False


def load_config(path):
    try:
        with open(path, 'r', encoding='utf8') as f:
            config = json.load(f)
            return config
    except:
        return {}


HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0",
    "Content-Type": "application/json;charset=utf-8",
}


async def get_nid(text: str, token) -> str:
    """获得文章id"""
    url = f'https://if.caiyunai.com/v2/novel/{token}/novel_save'
    data = {"content": text, "title": "", "ostype": ""}
    response = await aiorequests.post(url, json=data, headers=HEADER)
    if response.status_code == 200:
        res = await response.json()
        if res['status'] != 0:
            if res['status'] == -1:
                raise Exception('账号不存在，请更换apikey！')
            if res['status'] == -6:
                raise Exception('账号已被封禁，请更换apikey！')
            else:
                raise Exception(res['msg'])
        # print(res)
        return res['data']['nid'], res['data']['novel']['branchid'], res['data']['novel']['firstnode']
    else:
        raise Exception(f'HTTP {response.status_code}')


async def submit_to_ai(text: str, token, novel_id: str, branchid, firstnode, title="", model_id: str = '601f92f60c9aaf5f28a6f908'):
    """将文本提交到指定模型的AI，得到xid"""
    url = f'https://if.caiyunai.com/v2/novel/{token}/novel_ai'
    data = {
        "nid": novel_id,
        "content": text,
        "uid": token,
        "mid": model_id,
        "title": title,
        "ostype": "",
        "status": "http",
        "lang": "zh",
        "branchid": branchid,
        "lastnode": firstnode
    }
    response = await aiorequests.post(url, json=data, headers=HEADER)
    rsp_json = await response.json()
    # print(rsp_json)
    if rsp_json['status'] != 0:
        if rsp_json['status'] == -1:
            raise Exception('账号不存在，请更换apikey！')
        if rsp_json['status'] == -6:
            raise Exception('账号已被封禁，请更换apikey！')
        elif rsp_json['status'] == -5:
            raise Exception(
                f"存在不和谐内容，类型：{rsp_json['data']['label']}，剩余血量：{rsp_json['data']['total_count']-rsp_json['data']['shut_count']}")
        else:
            raise Exception(rsp_json['msg'])
    nodes = rsp_json['data']['nodes']
    return nodes


# async def poll_for_result(nid: str, xid: str, token):
#     """不断查询，直到服务器返回生成结果"""
#     url = 'https://if.caiyunai.com/v2/novel/{token}/novel_dream_loop'
#     data = {
#         "nid": nid,
#         "xid": xid,
#         "ostype": ""
#     }
#     max_retry_times = 10
#     for _ in range(max_retry_times):
#         response = await aiorequests.post(url, json=data, headers=HEADER)
#         rsp_json = await response.json()
#         print(rsp_json)
#         if rsp_json['status']!=0:
#             if rsp_json['status']==-6:
#                 raise Exception('账号被封禁')
#             else:
#                 raise Exception(rsp_json['msg'])
#         if rsp_json['data']['count'] != 0:  # 说明还没有生成好，继续重试
#             await asyncio.sleep(1.5)
#             continue
#         results = rsp_json['data']['rows']
#         results = [res['content'] for res in results]
#         return results
#     raise TimeoutError('服务器响应超时')


# async def get_single_continuation(text: str, token, title="", iter=3, mid='601f92f60c9aaf5f28a6f908'):
#     try:
#         result = ''
#         for i in range(iter): # 默认连续续写三次
#             if i == 0:
#                 result = text
#             else:
#                 asyncio.sleep(1)
#             try:
#                 nid, branchid,firstnode = await get_nid(result, token)
#                 nodes = await submit_to_ai(result, token, nid, branchid, firstnode, title=title, model_id=mid)
#                 #continuation = await poll_for_result(nid, xid, token)
#                 choose=random.choice(nodes)
#                 result += choose['content']
#             except Exception as e:
#                 if i:
#                     result=f'第{i+1}次迭代中断：{e}\n 当前续写结果：{result}......'
#                     return result
#                 else:
#                     raise Exception(e)
#         if result:
#             result="续写结果：\n" + result + '......'
#         return result
#     except Exception as e:
#         raise Exception(e)


async def add_node(nid, node, nodeids, token):
    """获得文章id"""
    url=f'https://if.caiyunai.com/v2/novel/{token}/add_node'
    data = {
                "nodeids": nodeids,
                "choose": node["_id"],
                "nid": nid,
                "value": node['content'],
                "ostype": "",
                "lang": "zh"
            }
    response = await aiorequests.post(url, json=data, headers=HEADER)
    if response.status_code == 200:
        res = await response.json()
        if res['status']!=0:
            if res['status']==-1:
                raise Exception('账号不存在，请更换apikey！')
            if res['status']==-6:
                raise Exception('账号已被封禁，请更换apikey！')
            else:
                raise Exception(res['msg'])
        #print(res)
        return
    else:
        raise Exception(f'HTTP {response.status_code}')


async def get_cont_continuation(text: str, token, title="", iter=3, mid='601f92f60c9aaf5f28a6f908'):
    try:
        result = text
        nid, branchid, lastnode = await get_nid(result, token)
        for i in range(iter):  # 默认连续续写三次
            asyncio.sleep(1)
            try:
                nodes = await submit_to_ai(result, token, nid, branchid, lastnode, title=title, model_id=mid)
                choose = random.choice(nodes)
                nodeids = []
                for node in nodes:
                    nodeids.append(node["_id"])
                result += choose['content']
                await add_node(nid, choose, nodeids, token)
                lastnode = choose["_id"]
            except Exception as e:
                if i:
                    result = f'第{i}次迭代中断：{e}\n 当前续写结果：{result}......'
                    return result
                else:
                    raise Exception(e)
        if result:
            result = "续写结果：\n" + result + '......'
        return result
    except Exception as e:
        raise Exception(e)
