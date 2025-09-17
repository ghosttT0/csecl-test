from django.utils import timezone
from django.db import IntegrityError
from interview.models import StudentApplication  # 导入模型


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
                "follow_direction": "发展方向"  # 匹配 Postman 中的 "direction"
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
                phone_number=data["phone_number"],  # 模型字段 phone_number ← 数据键名 phone
                gaokao_math=int(data["gaokao_math"]),  # 模型字段 gaokao_math ← 数据键名 math
                gaokao_english=int(data["gaokao_english"]),  # 模型字段 gaokao_english ← 数据键名 english
                follow_direction=data["follow_direction"],  # 模型字段 follow_direction ← 数据键名 direction
                good_at=data.get("good_at", ""),  # 可选字段
                reason=data.get("reason", ""),  # 可选字段
                future=data.get("future",""),
                book_time=data.get("book_time") or timezone.now()
            )

            # 4. 保存到数据库
            application.save()
            return True, f"申请成功！申请ID：{application.id}"

        except ValueError:
            return False, "数据格式错误：数学/英语成绩必须是数字"
        except IntegrityError:
            return False, "数据库错误：数据不符合表结构约束（如字段长度超限）"
        except Exception as e:
            return False, f"提交失败：{str(e)}"  # 捕获其他错误，便于调试

def rate_application(app_id, score):
        """管理员评分"""
        try:
            # 查询申请记录
            application = StudentApplication.objects.get(id=app_id)

            # 校验评分格式（示例：1-10分）
            if not (score.isdigit() and 1 <= int(score) <= 10):
                return False, "评分必须是1-10的数字"

            # 更新评分
            application.value = score
            application.save()
            return True, "评分成功"

        except StudentApplication.DoesNotExist:
            return False, "申请记录不存在"
        except Exception as e:
            return False, f"评分失败：{str(e)}"

def get_applications(filters=None):
        """查询申请记录（支持筛选）"""
        queryset = StudentApplication.objects.all().order_by("-book_time")  # 按申请时间倒序

        # 如果有筛选条件（如按方向、年级）
        if filters:
            if "direction" in filters:
                queryset = queryset.filter(follow_direction__icontains=filters["direction"])
            if "grade" in filters:
                queryset = queryset.filter(grade=filters["grade"])

        return queryset