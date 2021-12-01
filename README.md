# novel_ai_kai
适用hoshino的基于彩云小梦的小说AI续写插件

参考[KaguyaBot](https://github.com/liwh011/Kaguya-QQBot) 与[Novel_AI](https://github.com/pcrbot/Novel_AI)，移植到hoshino并适配新版彩云小梦api的小说AI续写插件。

因为彩云小梦恢复开放注册了就把之前缝了一半的东西搞完了。主要是增加了一些分群自定义项目，尤其是apikey分群设置，避免了一群作死导致key被ban害的所有群都无法使用的情况。

## 配置

目前默认apikey为空，即所有群在未单独设置apikey前都不能使用续写功能。如果想默认使用通用apikey可修改 novel.py 中templete的token项。

apikey获取：

- 前往 http://if.caiyunai.com/dream 注册彩云小梦用户；
- 注册完成后，在 chrome 浏览器地址栏输入 ``javascript:alert(localStorage.cy_dream_user)``，注意前缀javascript需单独复制粘贴；
- 弹出窗口中的uid即为apikey。

或者：

- 前往 http://if.caiyunai.com/dream 注册彩云小梦用户；
- 注册完成后，F12打开开发者工具；
- 进行一次续写；
- 在Network中查看novel_ai请求，Request Payload中uid项即为apikey。


## 用法

- ``(机器人昵称)续写 续写内容`` 进行续写。续写内容部分可用|分隔设置标题（``(机器人昵称)续写 标题|正文``），不过似乎标题能起到的引导效果很有限；
- ``默认续写迭代 (迭代次数)`` 修改本群默认续写迭代次数，默认为3；
- ``默认续写模型 (模型名)`` 修改本群默认续写人工智障模型，默认为小梦0号，后接要修改的模型名称，不接内容可查看可用模型列表；
- ``设置续写apikey (apikey)`` 设置本群apikey，后接要设置的新apikey，不接内容可查看apikey获取指南。

## 示例

![image](https://user-images.githubusercontent.com/55473115/144167346-da552952-2751-414d-b1bb-4fb326c89b13.png)

