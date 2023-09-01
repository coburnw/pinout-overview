import collections

colors = dict(
    black = {
        50: '#707b91',
        100: "#5f6167",
        200: "#424448",
        300: "#363431",
        400: "#26231d",
    },
    
    brown = {
        50 :  "#c68886",
        100 : "#b37472",
        200 : "#a45c59",
        300 : "#905a58",
        400 : "#7c5755"
    },
    
    red = {
        50 :  "#fc6565",
        100 : "#ee2b2b",
        200 : "#c11010",
        300 : "#911616",
        400 : "#661717"
    },
    
    orange = {
        50 :  "#ff8a2a",
        100 : "#f46f01",
        200 : "#c15701",
        300 : "#9c4a07",
        400 : "#7a3d0b"
    },
    
    yellow = {
        50 :  "#cdbd6a",
        100 : "#bdab54",
        200 : "#a99842",
        300 : "#928541",
        400 : "#7d7340"
    },
    
    green = {
        50 :  "#8ab96f",
        100 : "#77a55c",
        200 : "#658e4e",
        300 : "#5c794b",
        400 : "#536648"
    },
    
    blue = {
        50 :  "#8aaccc",
        100 : "#7599bb",
        200 : "#5985ae",
        300 : "#577a9b",
        400 : "#556f86"
    },
    
    violet = {
        50 :  "#ad8fc2",
        100 : "#9a7caf",
        200 : "#8764a0",
        300 : "#7a618c",
        400 : "#6e5e79"
    },

    white = {
        50 :  "#bfbfbf",
        100 : "#cfcfcf",
        200 : "#dfdfdf",
        300 : "#efefef",
        400 : "#ffffff"
    }
)

class Color():
    def __init__(self, hue, values):
        self.hue = hue
        self.values = values
        return

    def __getitem__(self, key):
        key = int(key / 10)
        return self.values[key]

    
if __name__ == '__main__':
    from v_palette import get_colors

    print(get_colors(("red", 100)))
    
    black = Color('black', [
        '#707b91',
        "#5f6167",
        "#424448",
        "#363431",
        "#26231d"
        ]
                                        )

    #White = collections.namedtuple('white', ['50', 'x100', 'x200', 'x300', 'x400'])
    #white = White._make(["#bfbfbf", "#cfcfcf", "#dfdfdf", "#efefef", "#ffffff"])

    print(black)
    print(black[3])
