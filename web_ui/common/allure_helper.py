"""
MallLite 自动化测试 - Allure 报告辅助模块
封装 Allure 常用操作，简化用例中的报告代码

用法：
    from common.allure_helper import AllureHelper

    # 添加标题和描述
    AllureHelper.title("登录功能", "验证管理员能正常登录")
    AllureHelper.severity("critical")

    # 添加测试步骤
    AllureHelper.step("打开登录页", lambda: page.goto("/login"))
    AllureHelper.step("输入用户名", lambda: page.fill("#username", "admin"))

    # 添加附件
    AllureHelper.attach_text("响应内容", response_text)
    AllureHelper.attach_json("接口响应", response_data)
    AllureHelper.attach_image("截图", screenshot_path)
"""

import json
import allure
from common.logger import get_logger

logger = get_logger("allure_helper")


class AllureHelper:
    """Allure 报告辅助工具类"""

    @staticmethod
    def title(title, description=""):
        """
        设置用例标题和描述

        参数：
            title: 用例标题
            description: 用例描述
        """
        allure.title(title)
        if description:
            allure.description(description)

    @staticmethod
    def severity(level="normal"):
        """
        设置用例优先级

        参数：
            level: blocker / critical / normal / minor / trivial
        """
        allure.dynamic.severity(getattr(allure.severity_level, level.upper(), allure.severity_level.NORMAL))

    @staticmethod
    def tag(tag_name):
        """添加标签"""
        allure.dynamic.tag(tag_name)

    @staticmethod
    def feature(feature_name):
        """设置功能模块"""
        allure.dynamic.feature(feature_name)

    @staticmethod
    def story(story_name):
        """设置用户故事"""
        allure.dynamic.story(story_name)

    @staticmethod
    def step(step_name, func=None):
        """
        添加测试步骤

        参数：
            step_name: 步骤描述
            func: 步骤执行的函数（可选，不传则只记录步骤名）

        用法：
            # 方式一：记录步骤名
            AllureHelper.step("验证登录成功")

            # 方式二：记录并执行
            AllureHelper.step("点击登录按钮", lambda: page.click("#login-btn"))
        """
        if func:
            with allure.step(step_name):
                try:
                    return func()
                except Exception as e:
                    logger.error(f"步骤 '{step_name}' 失败：{e}")
                    raise
        else:
            allure.attach(step_name, name="步骤", attachment_type=allure.attachment_type.TEXT)

    @staticmethod
    def attach_text(content, name="文本"):
        """附加文本内容"""
        allure.attach(str(content), name=name, attachment_type=allure.attachment_type.TEXT)

    @staticmethod
    def attach_json(data, name="JSON"):
        """附加 JSON 数据"""
        if isinstance(data, (dict, list)):
            content = json.dumps(data, ensure_ascii=False, indent=2)
        else:
            content = str(data)
        allure.attach(content, name=name, attachment_type=allure.attachment_type.JSON)

    @staticmethod
    def attach_html(content, name="HTML"):
        """附加 HTML 内容"""
        allure.attach(content, name=name, attachment_type=allure.attachment_type.HTML)

    @staticmethod
    def attach_image(filepath, name="截图"):
        """附加图片"""
        try:
            allure.attach.file(str(filepath), name=name, attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            logger.error(f"附加图片失败：{e}")

    @staticmethod
    def attach_request_log(method, url, headers=None, body=None, response=None, status_code=None):
        """
        附加接口请求日志（用于 API 测试或混合测试）

        参数：
            method: 请求方法
            url: 请求地址
            headers: 请求头
            body: 请求体
            response: 响应内容
            status_code: 状态码
        """
        log_parts = [f"【{method} {url}】"]

        if headers:
            log_parts.append(f"请求头：{json.dumps(headers, ensure_ascii=False, indent=2)}")
        if body:
            log_parts.append(f"请求体：{json.dumps(body, ensure_ascii=False, indent=2) if isinstance(body, dict) else body}")
        if status_code is not None:
            log_parts.append(f"状态码：{status_code}")
        if response:
            log_parts.append(f"响应：{json.dumps(response, ensure_ascii=False, indent=2) if isinstance(response, dict) else response}")

        content = "\n".join(log_parts)
        allure.attach(content, name="接口请求日志", attachment_type=allure.attachment_type.TEXT)

    @staticmethod
    def page_info(page):
        """
        附加页面信息（URL、标题、Console 日志）

        参数：
            page: Playwright 的 page 对象
        """
        info = f"URL：{page.url}\n标题：{page.title()}"
        allure.attach(info, name="页面信息", attachment_type=allure.attachment_type.TEXT)