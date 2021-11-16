# -*- coding: utf-8 -*-
# @Description:
# @author: victor
# @create time: 2021-08-20-8:10 下午
from Go.agent.naive import RandomBot
from Go.web_fronted.server import get_web_app

random_agent = RandomBot()
web_app = get_web_app({'random': random_agent})
web_app.run()
