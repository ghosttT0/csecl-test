from django.utils import timezone
from django.db import IntegrityError
from interview.models import StudentApplication  # 导入模型
from django.core.cache import cache


"""学生申请业务逻辑类"""

def submit_application(data):
        """
        学生提交申请
        :param data: 包含申请信息的字典（如 name, number 等）
        :return: (是否成功, 消息)
        """
        try:
            # 1. 关键参数校验（非空校验，与 Postman 数据的键名匹配）
            required_fields = {
                "number": "学号",
                "grade": "年级",
                "phone_number":"电话",
                "gaokao_math": "高考数学成绩",  # 匹配 Postman 中的 "math"
                "gaokao_english": "高考英语成绩",  # 匹配 Postman 中的 "english"
                "follow_direction": "发展方向" , # 匹配 Postman 中的 "direction"
                "email":"邮件"
            }
            # 检查必填字段是否缺失
            for key, field_name in required_fields.items():
                if not data.get(key):
                    return False, f"{field_name}不能为空"

            # 2. 业务规则：检查学号是否已提交
            if StudentApplication.objects.filter(number=data["number"]).exists():
                return False, "该学号已提交过申请"

            # 3. 处理数据（映射到模型字段）
            application = StudentApplication(
                name=data.get("name", ""),  # 可选字段，默认空字符串
                number=data["number"],
                grade=data["grade"],
                phone_number=data["phone_number"],
                gaokao_math=int(data["gaokao_math"]),
                gaokao_english=int(data["gaokao_english"]),
                follow_direction=data["follow_direction"],
                good_at=data.get("good_at", ""),  # 可选字段
                reason=data.get("reason", ""),  # 可选字段
                experience=data.get("experience",""),
                major=data.get("major",""),
                email=data.get("email",""),
                other_lab=data.get("other_lab",""),
                future=data.get("future",""),
                book_time=data.get("book_time") or timezone.now()
            )

            # 4. 保存到数据库
            application.save()
            return True, f"申请成功！申请ID：{application.id}"

        except ValueError:
            return False, "数据格式错误"
        except IntegrityError:
            return False, "数据库错误：数据不符合表结构约束（如字段长度超限）"
        except Exception as e:
            return False, f"提交失败：{str(e)}"  # 捕获其他错误，便于调试

def get_applications(student_number):
    try:
        # 根据学号查询记录（假设 number 是模型的字段）
        student = StudentApplication.objects.get(number=student_number)
    except StudentApplication.DoesNotExist:
        return False, "请输入学号"

    # 发布/隐藏控制：未发布则不允许查询
    released = cache.get('interview_results_released', False)
    if not released:
        return False, "面试结果尚未发布，请稍后再试"

    # 提取 value 值并判断
    value = student.value
    message = ""

    if value is None:
        message = "不要着急哦，你的面试成绩还在运输中，等等再来查询吧"
    elif float(value) < 85:  # 假设 value 是字符串，转成 float 比较；若为整数，用 int
        message = "很遗憾，您的面试没能通过，希望下次能有更好的成绩"
    else:
        message = "恭喜你，通过面试啦！快去注册属于你的实验室账户吧"


    return True, message