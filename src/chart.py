import pandas as pd
from pyecharts import options as opts
from pyecharts.globals import *
from pyecharts.charts import *
import numpy as np

class Chart:
    colors = [
        '#111111',
        '#f06020',
        '#1ac6bc',
        '#cc1b9e',
        '#bde01e',
        '#211ac6',
        '#f0bd20',
        '#791ac6',
        '#f0e620',
        '#e61f2e',
        '#38cb1b',
        '#74d3ff',
        '#ffb174',
        '#678ce3',
        '#ffcd74',
        '#8867e3',
        '#ffe974',
        '#cf67e3',
        '#b9ee6c',
        '#ff7f74',
        '#ed6ca1',
        '#67e384',
        '#ff7f74'
    ]

    def __init__(self):
        pass

    def get_kline(self, xdatas, kdatas, stock_info) -> Kline:
        c = (
            Kline(
                init_opts=opts.InitOpts(
                )
            )
                .add_xaxis(xaxis_data=xdatas)
                .add_yaxis(
                series_name='kline',
                y_axis=kdatas
            )
                .set_global_opts(
                title_opts=opts.TitleOpts(
                    title=stock_info['name'],
                    subtitle=stock_info['symbol'],
                ),
                xaxis_opts=opts.AxisOpts(
                    is_scale=True,
                    type_="category",
                    splitarea_opts=opts.SplitAreaOpts(
                        is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                    ),
                ),
                yaxis_opts=opts.AxisOpts(
                    is_scale=True,
                    splitarea_opts=opts.SplitAreaOpts(
                        is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                    ),
                ),
                legend_opts=opts.LegendOpts(
                    is_show=False, pos_bottom=10, pos_left="center"
                ),
                datazoom_opts=[
                    opts.DataZoomOpts(
                        is_show=True,
                        xaxis_index=[0, 1, 2],
                        type_="slider",
                        pos_top="90%",
                        range_start=90,
                        range_end=100,
                    ),
                    #                 opts.DataZoomOpts(
                    #                     is_show=True,
                    #                     yaxis_index=[0],
                    #                     type_="slider",
                    #                     orient = 'vertical',
                    # #                     pos_top="90%",
                    #                     pos_right="0%",
                    #                     range_start=0,
                    #                     range_end=100,
                    #                 ),
                ],
                tooltip_opts=opts.TooltipOpts(
                    trigger="axis",
                    axis_pointer_type="cross",
                    background_color="rgba(245, 245, 245, 0.8)",
                    border_width=1,
                    border_color="#ccc",
                    textstyle_opts=opts.TextStyleOpts(color="#000"),
                ),
                visualmap_opts=opts.VisualMapOpts(
                    is_show=True,
                    dimension=2,
                    series_index=[5, 6, 7, 8, 9, 10,11,12],
                    is_piecewise=True,
                    pieces=[
                        {"value": 1, "color": "#ff7f74"},
                        {"value": -1, "color": "#67e384"},
                    ],
                ),
                axispointer_opts=opts.AxisPointerOpts(
                    is_show=True,
                    link=[{"xAxisIndex": "all"}],
                    label=opts.LabelOpts(background_color="#777"),
                ),
                brush_opts=opts.BrushOpts(
                    x_axis_index="all",
                    brush_link="all",
                    out_of_brush={"colorAlpha": 0.1},
                    brush_type="lineX",
                ),
            )
        )
        return c

    def get_line(self, xdatas, data_dic):
        line = Line()
        line.add_xaxis(xaxis_data=xdatas)
        i = 0
        for key in data_dic:
            value = data_dic[key];
            line.add_yaxis(
                series_name=value['name'],
                y_axis=value['datas'],
                symbol="none",
                is_smooth=True,
                is_hover_animation=False,
                linestyle_opts=opts.LineStyleOpts(width=2, opacity=0.9),
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(color=Chart.colors[i]),
            )
            i += 1

        line.set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
        return line

    def get_volome(self, xdatas, vols, kdatas):
        bar = (
            Bar(init_opts=opts.InitOpts())
                .add_xaxis(xaxis_data=xdatas)
                .add_yaxis(
                series_name="Volume",
                yaxis_data=[
                    [i, vols[i], 1 if kdatas[i][0] > kdatas[i][1] else -1]
                    for i in range(len(kdatas))
                ],
                #         yaxis_data = vols,
                xaxis_index=1,
                yaxis_index=1,
                label_opts=opts.LabelOpts(is_show=False)
            )
                .set_global_opts(
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    is_scale=True,
                    grid_index=1,
                    boundary_gap=False,
                    axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                    axistick_opts=opts.AxisTickOpts(is_show=False),
                    splitline_opts=opts.SplitLineOpts(is_show=False),
                    axislabel_opts=opts.LabelOpts(is_show=False),
                    split_number=20,
                    min_="dataMin",
                    max_="dataMax",
                ),
                yaxis_opts=opts.AxisOpts(
                    grid_index=1,
                    is_scale=True,
                    split_number=2,
                    axislabel_opts=opts.LabelOpts(is_show=False),
                    axisline_opts=opts.AxisLineOpts(is_show=True),
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                legend_opts=opts.LegendOpts(is_show=False),
            )
        )
        return bar

    def get_sar(self, df, ty):
        t_color = "#f09320"
        if ty == 'up':
            t_color = "#1ac6bc"

        esSar = (
            Scatter()
                .add_xaxis(df.trade_date.tolist())
                .add_yaxis(
                "sar", df.sar.to_numpy().round(2).tolist(),
                symbol_size=5,
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(color=t_color),
            )
                .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
            #     .set_global_opts(title_opts=opts.TitleOpts(title="EffectScatter-基本示例"))
        )
        return esSar

    def get_stop_price_chart(self, df):
        t_color = "#0bcf3d"
        esSar = (
            Scatter()
                .add_xaxis(df.trade_date.tolist())
                .add_yaxis(
                "stop_price", df['stop_price'].to_numpy().round(2).tolist(),
                symbol_size=5,
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(color=t_color),
            )
                .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
            #     .set_global_opts(title_opts=opts.TitleOpts(title="EffectScatter-基本示例"))
        )
        return esSar

    def get_bs(self, df, ty):
        t_color = "#0c9bdf"
        symbol = SymbolType.TRIANGLE
        if ty == 'buy':
            t_color = "#f20d68"
            symbol = SymbolType.ROUND_RECT

        esSar = (
            EffectScatter()
                .add_xaxis(df.trade_date.tolist())
                .add_yaxis(
                ty, df['unit_price'].to_numpy().round(2).tolist(),
                symbol_size=10,
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(color=t_color),
                symbol=symbol
            )
                .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
            #     .set_global_opts(title_opts=opts.TitleOpts(title="EffectScatter-基本示例"))
        )
        return esSar

    def get_grid(self, stock_info, xdatas, kdatas, linetec_dic, vols, sar=None, bs=None, df_stop_price=None):
        kline = self.get_kline(xdatas, kdatas, stock_info)
        line = self.get_line(xdatas, linetec_dic)
        bar = self.get_volome(xdatas, vols, kdatas)

        if sar is not None:
            sar_up = self.get_sar(sar['up'], 'up');
            kline.overlap(sar_up)

            sar_down = self.get_sar(sar['down'], 'down');
            kline.overlap(sar_down)

        if bs is not None:
            bs_b = self.get_bs(bs['buy'], 'buy')
            kline.overlap(bs_b)
            bs_s = self.get_bs(bs['sell'], 'sell')
            kline.overlap(bs_s)

        if df_stop_price is not None:
            stop_p = self.get_stop_price_chart(df_stop_price)
            kline.overlap(stop_p)

        overlap_kline_line = kline.overlap(line)
        grid_chart = Grid(
            init_opts=opts.InitOpts(
                width="900px",
                height="800px",
            )
        )
        grid_chart.add(
            overlap_kline_line,
            grid_opts=opts.GridOpts(pos_left="6%", pos_right="8%", height="55%"),
        )

        grid_chart.add(
            bar,
            grid_opts=opts.GridOpts(
                pos_left="6%", pos_right="8%", pos_top="65%", height="10%"
            ),
        )

        return grid_chart

    def get_macd_chart(self, xdatas, dif, dem, ocr):

        line = Line()
        line.add_xaxis(xaxis_data=xdatas)
        line.add_yaxis(
            series_name='dif',
            y_axis=dif,
            symbol="none",
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=2, opacity=0.9),
            label_opts=opts.LabelOpts(is_show=False),
            itemstyle_opts=opts.ItemStyleOpts(color=Chart.colors[0]),
        )
        line.add_yaxis(
            series_name='dem',
            y_axis=dem,
            symbol="none",
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=2, opacity=0.9),
            label_opts=opts.LabelOpts(is_show=False),
            itemstyle_opts=opts.ItemStyleOpts(color=Chart.colors[1]),
        )
        line.set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
        bar = (
            Bar()
                .add_xaxis(xaxis_data=xdatas)
                .add_yaxis(
                series_name="ocr",
                yaxis_data=[
                    [i, ocr[i], 1 if ocr[i] > 0 else -1]
                    for i in range(len(ocr))
                ],
                #         yaxis_data = vols,
                xaxis_index=1,
                yaxis_index=1,
                label_opts=opts.LabelOpts(is_show=False)
            )
                .set_global_opts(
                title_opts=opts.TitleOpts(
                    title='MACD',
                    title_textstyle_opts=opts.TextStyleOpts(font_size=10),
                    pos_top="75%",
                ),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    is_scale=True,
                    grid_index=2,
                    boundary_gap=False,
                    #                 axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                    #                 axistick_opts=opts.AxisTickOpts(is_show=False),
                    #                 splitline_opts=opts.SplitLineOpts(is_show=False),
                    #                 axislabel_opts=opts.LabelOpts(is_show=False),
                    split_number=20,
                    #                 min_="dataMin",
                    #                 max_="dataMax",
                ),
                yaxis_opts=opts.AxisOpts(
                    grid_index=2,
                    is_scale=True,
                    split_number=2,
                    #                 axislabel_opts=opts.LabelOpts(is_show=False),
                    #                 axisline_opts=opts.AxisLineOpts(is_show=False),
                    #                 axistick_opts=opts.AxisTickOpts(is_show=False),
                    #                 splitline_opts=opts.SplitLineOpts(is_show=False),
                ),
                legend_opts=opts.LegendOpts(is_show=False),
            )
        )
        bar.overlap(line)
        return bar

    def get_dma_chart(xdatas, ddd, ama):
        line = Line()
        line.add_xaxis(xaxis_data=xdatas)
        line.add_yaxis(
            series_name='ddd',
            y_axis=ddd,
            symbol="none",
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=2, opacity=0.9),
            label_opts=opts.LabelOpts(is_show=False),
            itemstyle_opts=opts.ItemStyleOpts(color=Chart.colors[0]),
        )
        line.add_yaxis(
            series_name='ama',
            y_axis=ama,
            symbol="none",
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=2, opacity=0.9),
            label_opts=opts.LabelOpts(is_show=False),
            itemstyle_opts=opts.ItemStyleOpts(color=Chart.colors[1]),
        )
        line.set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
        return line

    def get_line_ba(self,df, init_account, stock_info):
        trade_dates = np.array(df.trade_date).tolist()
        balances = np.array((df['balance'] - init_account) / init_account).tolist()
        c = (
            Line()
                .add_xaxis(trade_dates)
                .add_yaxis("p"
                           , balances
                           , is_smooth=True,
                           is_hover_animation=False,
                           linestyle_opts=opts.LineStyleOpts(width=2, opacity=0.9),
                           label_opts=opts.LabelOpts(is_show=False),
                           )
                .set_global_opts(
                title_opts=opts.TitleOpts(title=stock_info['name'],subtitle=stock_info['symbol']),
                xaxis_opts=opts.AxisOpts(
                    is_scale=True,
                    type_="category",
                    splitarea_opts=opts.SplitAreaOpts(
                        is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                    ),
                ),
                yaxis_opts=opts.AxisOpts(
                    is_scale=True,
                    splitarea_opts=opts.SplitAreaOpts(
                        is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                    ),
                ),
                datazoom_opts=[
                    opts.DataZoomOpts(
                        is_show=True,
                        # xaxis_index=[0],
                        type_="slider",
                        # pos_top="90%",
                        range_start=0,
                        range_end=100,
                    ),
                    #                 opts.DataZoomOpts(
                    #                     is_show=True,
                    #                     yaxis_index=[0],
                    #                     type_="slider",
                    #                     orient = 'vertical',
                    # #                     pos_top="90%",
                    #                     pos_right="0%",
                    #                     range_start=0,
                    #                     range_end=100,
                    #                 ),
                ],
                tooltip_opts=opts.TooltipOpts(
                    trigger="axis",
                    axis_pointer_type="cross",
                    background_color="rgba(245, 245, 245, 0.8)",
                    border_width=1,
                    border_color="#ccc",
                    textstyle_opts=opts.TextStyleOpts(color="#000"),
                ),
            )
        )
        return c

