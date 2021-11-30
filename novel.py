import os

from hoshino import Service, priv
from hoshino.typing import CQEvent
from .novel_data import get_cont_continuation, load_config, save_config
from hoshino.util import FreqLimiter, DailyNumberLimiter

config_path = os.path.join(os.path.dirname(__file__), 'naconfig.json')

if not os.path.exists(config_path):
    with open(config_path, 'w', encoding='utf8') as f:
        f.write("{}")
config = load_config(config_path)

sv_help = '''
基于彩云小梦的小说续写功能
[续写 标题(可选)|续写内容] 人工智障续写小说
[默认续写迭代 (迭代次数)] 修改本群默认续写迭代次数，默认为3
[默认续写模型 (模型名)] 修改本群默认续写人工智障模型，默认为小梦0号
[设置续写apikey] 设置本群apikey，具体指南请发送该命令查看
'''.strip()

sv = Service('novel-ai', bundle='娱乐', help_=sv_help,
             manage_priv=50, enable_on_default=False)

model_list = {"小梦0号": "60094a2a9661080dc490f75a",
              "小梦1号": "601ac4c9bd931db756e22da6",
              "纯爱小梦": "601f92f60c9aaf5f28a6f908",
              "言情小梦": "601f936f0c9aaf5f28a6f90a",
              "玄幻小梦": "60211134902769d45689bf75"}


# default_key="602c8c0826a17bcd889faca7"    #already banned

templete = {'iter': 3, 'model': '小梦0号', 'token': ''}   

DAILY = 15

flmt = FreqLimiter(60)
dlmt = DailyNumberLimiter(DAILY)


@sv.on_prefix('续写', only_to_me=True)
async def novel_continue_rec(bot, ev: CQEvent):
    global config

    uid = ev.user_id
    gid = str(ev.group_id)
    if gid not in config:
        config[gid] = templete
        save_config(config, config_path)

    if not priv.check_priv(ev, priv.SUPERUSER):
        if not dlmt.check(uid):
            await bot.finish(ev, f'您今天已经进行{DAILY}轮迭代了，休息一下明天再来吧~', at_sender=True)
        if not flmt.check(gid):
            await bot.finish(ev, f'本群续写功能冷却中~请{int(flmt.left_time(gid)) + 1}秒后再来~)', at_sender=True)

    if not config[gid]['token']:
        await bot.finish(ev, f'本群续写apikey未设置！请使用‘设置续写apikey’指令设置本群apikey！')

    text = ev.message.extract_plain_text().strip()
    if not text:
        await bot.finish(ev, '请附带需要续写的内容！')
    title = ""
    if "|" in text:
        title = text.split("|")[0]
        text = text.split("|")[1]

    iter = config[gid]['iter']
    token = config[gid]['token']

    now = DAILY-dlmt.get_num(uid)
    if iter > now:
        if now:
            await bot.send(ev, f'您的迭代限额仅剩{now}次了~')
            iter = now
        else:
            await bot.finish(ev, f'您今天已经进行{DAILY}轮迭代了，休息一下明天再来吧~', at_sender=True)
            dlmt.increase(uid, int(iter))

    await bot.send(ev, '请稍等片刻~')
    mid = model_list[config[gid]['model']]
    try:
        res = await get_cont_continuation(text, token, title=title, iter=iter, mid=mid)
        if res:
            await bot.send(ev, res)
            flmt.start_cd(gid, 60)
            dlmt.increase(uid, int(iter))
    except Exception as e:
        await bot.send(ev, f'发生错误：{e}')
        if str(e)[11:17] == 'Polity':
            await bot.send(ev, f'涉政违禁内容将导致apikey快速被封！请自重！')
            try:
                await bot.set_group_ban(group_id=ev.group_id, user_id=ev.user_id, duration=60*(10))
            except:
                pass


@sv.on_prefix('默认续写迭代')
async def novel_iteration(bot, ev: CQEvent):
    global config

    if not priv.check_priv(ev, priv.ADMIN):
        await bot.send(ev, '此命令仅管理员可用~')
        return
    uid = ev.user_id
    gid = str(ev.group_id)
    if gid not in config:
        config[gid] = {'iter': 3, 'model': '小梦0号', 'token': ''}
        save_config(config, config_path)

    text = ev.message.extract_plain_text().strip()
    if not text:
        await bot.send(ev, f'请输入默认续写迭代次数！当前默认迭代次数：{config[gid]["iter"]}')
        return
    if text.isdigit():
        if int(text) > 5:
            await bot.send(ev, '最高只能迭代5次~')
            text = 5
        if int(text) < 1:
            await bot.send(ev, '最少迭代1次~')
            text = 1
        config[gid]['iter'] = int(text)
        save_config(config, config_path)
        await bot.send(ev, f'本群默认续写迭代次数已修改为{text}次！')
        return
    else:
        await bot.send(ev, '迭代次数仅接受纯数字，请重新输入！')
        return


@sv.on_prefix('默认续写模型')
async def novel_iteration(bot, ev: CQEvent):
    global config
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.send(ev, '此命令仅管理员可用~')
        return
    uid = ev.user_id
    gid = str(ev.group_id)
    if gid not in config:
        config[gid] = templete
        save_config(config, config_path)

    text = ev.message.extract_plain_text().strip()
    if not text:
        await bot.send(ev, f"请选择默认续写模型！当前模型：{config[gid]['model']}\n 可用模型：{','.join(model_list.keys())}")
        return
    if text in model_list:
        config[gid]['model'] = text
        save_config(config, config_path)
        await bot.send(ev, f'本群默认续写模型已修改为{text}！')
        return
    else:
        await bot.send(ev, f"未找到该模型，请重新输入！\n 可用模型：{','.join(model_list.keys())}")
        return


@sv.on_prefix('设置续写apikey')
async def novel_iteration(bot, ev: CQEvent):
    global config
    uid = ev.user_id
    gid = str(ev.group_id)
    if gid not in config:
        config[gid] = templete
        save_config(config, config_path)

    text = ev.message.extract_plain_text().strip()
    if not text:
        await bot.finish(ev, f'要设置apikey请在此命令后加上key！\n\napikey获取教程：\n1、前往 http://if.caiyunai.com/dream 注册彩云小梦用户；\n2、注册完成后，在 chrome 浏览器地址栏输入 javascript:alert(localStorage.cy_dream_user)，（前缀javascript需单独复制），弹出窗口中的uid即为apikey')
    try:
        if len(text) != 24:
            raise
        int(text, base=16)
    except:
        await bot.finish(ev, f'apikey格式有误!')

    config[gid]['token'] = str(text)
    save_config(config, config_path)
    await bot.send(ev, f'本群apikey已设置！')
