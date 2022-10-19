import matplotlib.pyplot as plt
import os
from pathlib import Path

BASE_PATH = Path(os.path.realpath(__file__)).parent.parent / 'img'

plt.style.use('seaborn-white')

# # *********************************** data **********************************************
name = 'exp-comp'
x_l = '#Samples'
y_l = 'Time (s)'
x = [20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300, 320, 340, 360, 380, 400]
y = [
    {
        'label': r'Computation cost of this work',
        'cl': 'b.-',
        'ys': [0.006001949310302734, 0.01199960708618164, 0.018973112106323242, 0.025972843170166016, 0.03397250175476074, 0.04199624061584473, 0.049001455307006836, 0.05700063705444336, 0.0630028247833252, 0.07000279426574707, 0.07700252532958984, 0.08300042152404785, 0.0910029411315918, 0.09799981117248535, 0.1040029525756836, 0.11000204086303711, 0.11700034141540527, 0.1250019073486328, 0.13200068473815918, 0.14000153541564941],
    },
    {
        'label': r'Computation cost of HE-based method',
        'cl': 'g.-',
        'ys': [13.423310041427612, 27.00786805152893, 42.14134502410889, 57.53962588310242, 73.44236660003662, 90.632483959198, 108.45700645446777, 127.27332711219788, 144.4138035774231, 161.90819811820984, 178.95950722694397, 195.746440410614, 212.9769208431244, 230.4174132347107, 246.50124883651733, 260.48227977752686, 277.7992615699768, 295.1454975605011, 312.668071269989, 331.20997977256775],
    },
]
# *********************************** draw **********************************************
font_family = 'Times New Roman'
font_size = 26
font_dict = {'family': font_family, 'size': font_size}

fig, ax1 = plt.subplots(figsize=(12, 8))
ax1.set_xlabel(x_l, fontdict=font_dict)
ax1.set_ylabel(y_l, fontdict=font_dict)

# plt.figure(figsize=(12, 8))
# plt.tick_params(labelright=True)

for i in y[:2]:
    ax1.plot(x, i['ys'], i['cl'], label=i['label'])

# plt.xlabel(x_l, fontdict=font_dict)
# plt.ylabel(y_l, fontdict=font_dict)

plt.xticks(fontproperties=font_family, size=font_size - 2)
plt.yticks(fontproperties=font_family, size=font_size - 2)

ax1.legend(loc='upper left', bbox_to_anchor=(0, 1), prop={'family': font_family, 'size': 18})

plt.savefig(BASE_PATH / f'{name}.pdf', bbox_inches='tight')
plt.show()