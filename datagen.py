import pandas as pd
import random
from faker import Faker
import datetime
from pathlib import Path

fake = Faker("vi_VN")
df = pd.read_csv(Path(__file__).parent / "chi_tieu_mau.csv")


def create_fakedata(id, name):
    categories = ["Ăn uống", "Di chuyển", "Mua sắm", "Giải trí", "Học tập", "Y tế", "Khác"]
    data = []
    start_date = datetime.date(2024, 1, 1)
    end_date = datetime.date(2024, 12, 31)
    for _ in range(1000):  # Tạo 1k giao dịch
        date = fake.date_between(start_date, end_date)
        category = random.choice(categories)
        amount = random.randint(20000, 500000)
        note = random.choice(
            ["Chi phí cần thiết trong tháng", "Thanh toán dịch vụ", "Khoản chi đột xuất", "Phí dịch vụ hoặc tiện ích"])
        data.append([id, date, name, category, amount, note])

    newdata = pd.DataFrame(data, columns=['Mã sinh viên', "Ngày", 'Tên', "Danh Mục", "Số Tiền", "Ghi Chú"])
    newdata["Ngày"] = pd.to_datetime(newdata["Ngày"], format=r'%Y-%m-%d')
    newdata = pd.concat([newdata, df])
    newdata.to_csv("chi_tieu_mau.csv", index=False)
    return 0


df['Ngày'] = pd.to_datetime(df["Ngày"], format=r'%Y-%m-%d')
df.to_csv("chi_tieu_mau.csv", index=False)
