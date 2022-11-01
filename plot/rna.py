import matplotlib.pyplot as plt
import os
from pathlib import Path

BASE_PATH = Path(os.path.realpath(__file__)).parent.parent / 'img'

plt.style.use('seaborn-white')

# # *********************************** data **********************************************
name = 'exp-rna'
x_l = '#Samples'
y_l = 'Time (ms)'
x = list(range(1, 401, 20))
y = [
    {
        'label': r'The proposed framework',
        'cl': 'b.-',
        'ys': [1.8587112426757812, 32.84740447998047, 63.95554542541504, 94.99669075012207, 125.88763236999512, 157.05013275146484, 188.246488571167, 219.7580337524414, 251.38306617736816, 282.6402187347412, 313.8427734375, 345.03626823425293, 376.28626823425293, 407.79638290405273, 438.8408660888672, 470.5390930175781, 501.6627311706543, 532.9074859619141, 563.9712810516357, 594.9711799621582],
    },
    {
        'label': r'OSDTI',
        'cl': 'g^-',
        'ys': [99.19357299804688, 908.1454277038574, 1677.4218082427979, 2451.5340328216553, 3265.78426361084, 4065.5620098114014, 4854.558944702148, 5635.4076862335205, 6427.935361862183, 7220.906496047974, 7975.9087562561035, 8697.603225708008, 9420.38607597351, 10150.823831558228, 10898.694276809692, 11669.111967086792, 12431.759119033813, 13104.270458221436, 13837.108612060547, 14564.025402069092],
    },
    # {
    #     'label': r'HE-based method',
    #     'cl': 'rs-',
    #     'ys': [1283.7529182434082, 13917.329549789429, 26539.25395011902, 39118.94392967224, 51751.46389007568, 64329.05292510986, 77076.9248008728, 90017.9991722107, 102834.43069458008, 115642.68779754639, 128412.41145133972, 141002.2132396698, 153567.9099559784, 166136.97171211243, 178976.79114341736, 191664.02173042297, 204237.23483085632, 216827.61216163635, 229443.0913925171, 242016.34550094604],
    # },
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

for i in y:
    ax1.plot(x, i['ys'], i['cl'], label=i['label'])

# plt.xlabel(x_l, fontdict=font_dict)
# plt.ylabel(y_l, fontdict=font_dict)

plt.xticks(fontproperties=font_family, size=font_size - 2)
plt.yticks(fontproperties=font_family, size=font_size - 2)

ax1.legend(loc='upper left', bbox_to_anchor=(0, 1), prop={'family': font_family, 'size': 18})

plt.savefig(BASE_PATH / f'{name}.eps', bbox_inches='tight')
plt.show()
