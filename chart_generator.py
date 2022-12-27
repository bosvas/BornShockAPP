import matplotlib

matplotlib.use('svg')
import matplotlib.pyplot as plt
import io
import base64


def make_chart(quake_list, name):
    x = []
    y = []
    for quake in quake_list:
        x.append(quake[3])
        y.append(quake[2])

    plt.plot_date(x, y, label=name, linestyle='solid')
    plt.gcf().autofmt_xdate()

    plt.title('Earthquakes magnitude on the week you were born')
    plt.xlabel('DateTime')

    plt.ylabel('Magnitude')

    plt.legend()

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)

    plot_url = base64.b64encode(img.getvalue()).decode()

    plt.cla()

    return plot_url
