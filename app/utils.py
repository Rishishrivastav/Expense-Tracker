import matplotlib.pyplot as plt
import io
import base64

def generate_pie_chart(transactions):
    income = sum(t.amount for t in transactions if t.type == 'Income')
    expense = sum(t.amount for t in transactions if t.type == 'Expense')
    labels = ['Income', 'Expense']
    sizes = [income, expense]
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%')
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return base64.b64encode(img.read()).decode('utf-8')
