import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import color as color_comp, display, font, sensor, text_sensor, time
from esphome.const import CONF_ID

CONF_DISPLAY_ID = "display_id"
CONF_TIME_ID = "time_id"
CONF_TEXT_FONT = "text_font"
CONF_ICON_FONT = "icon_font"
CONF_MAX_PAGES = "max_pages"
CONF_DELIMITER = "delimiter"
CONF_ROTATION_INTERVAL = "rotation_interval"
CONF_EXPIRY_INTERVAL = "expiry_interval"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_SHOW_WEATHER = "show_weather"
CONF_WEATHER_STATE = "weather_state"
CONF_SUN_ELEVATION = "sun_elevation"
CONF_WIFI_SIGNAL = "wifi_signal"
CONF_WIFI_IP = "wifi_ip"
CONF_FOOTER_LEFT = "footer_left"
CONF_FOOTER_RIGHT = "footer_right"
CONF_MAX_HEADERS = "max_headers"
CONF_HEADER_ROTATION_INTERVAL = "header_rotation_interval"
CONF_ACCENT_DAY = "accent_day"
CONF_ACCENT_NIGHT = "accent_night"
CONF_BACKGROUND_COLOR = "background_color"
CONF_TITLE_COLOR = "title_color"
CONF_SUBTITLE_COLOR = "subtitle_color"
CONF_DETAIL_COLOR = "detail_color"
CONF_SHOW_TIME = "show_time"
CONF_SHOW_DEFAULT_HEADER = "show_default_header"
CONF_DEFAULT_HEADER_TITLE = "default_header_title"
CONF_DEFAULT_HEADER_SUBTITLE = "default_header_subtitle"
CONF_TEXT_FONT_LARGE = "text_font_large"
CONF_TIME_ICON_FONT = "time_icon_font"
CONF_TIME_FORMAT = "time_format"
CONF_DATE_FORMAT = "date_format"

DEPENDENCIES = ["api", "display", "time"]
AUTO_LOAD = ["font", "sensor", "text_sensor"]


display_framework_ns = cg.esphome_ns.namespace("display_framework")
DisplayFramework = display_framework_ns.class_("DisplayFramework", cg.Component)

CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.Required(CONF_ID): cv.declare_id(DisplayFramework),
            cv.Required(CONF_DISPLAY_ID): cv.use_id(display.Display),
            cv.Required(CONF_TIME_ID): cv.use_id(time.RealTimeClock),
            cv.Optional(CONF_TEXT_FONT, default="text_font_14"): cv.use_id(font.Font),
            cv.Optional(CONF_ICON_FONT, default="icon_font_48"): cv.use_id(font.Font),
            cv.Optional(CONF_MAX_PAGES, default=5): cv.int_range(min=1, max=10),
            cv.Optional(CONF_DELIMITER, default="-|-"): cv.string,
            cv.Optional(CONF_ROTATION_INTERVAL, default="20s"): cv.positive_time_period_milliseconds,
            cv.Optional(CONF_EXPIRY_INTERVAL, default="10s"): cv.positive_time_period_milliseconds,
            cv.Optional(CONF_UPDATE_INTERVAL, default="1s"): cv.positive_time_period_milliseconds,
            cv.Optional(CONF_SHOW_WEATHER, default=True): cv.boolean,
            cv.Optional(CONF_SHOW_TIME, default=True): cv.boolean,
            cv.Optional(CONF_SHOW_DEFAULT_HEADER, default=True): cv.boolean,
            cv.Optional(CONF_DEFAULT_HEADER_TITLE): cv.string,
            cv.Optional(CONF_DEFAULT_HEADER_SUBTITLE): cv.string,
            cv.Optional(CONF_TEXT_FONT_LARGE): cv.use_id(font.Font),
            cv.Optional(CONF_TIME_ICON_FONT): cv.use_id(font.Font),
            cv.Optional(CONF_TIME_FORMAT, default="%H:%M:%S"): cv.string,
            cv.Optional(CONF_DATE_FORMAT, default="%d.%m"): cv.string,
            cv.Optional(CONF_WEATHER_STATE): cv.use_id(text_sensor.TextSensor),
            cv.Optional(CONF_SUN_ELEVATION): cv.use_id(sensor.Sensor),
            cv.Optional(CONF_WIFI_SIGNAL): cv.use_id(sensor.Sensor),
            cv.Optional(CONF_WIFI_IP): cv.use_id(text_sensor.TextSensor),
            cv.Optional(CONF_FOOTER_LEFT, default="ip"): cv.one_of("none", "ip", "wifi", lower=True),
            cv.Optional(CONF_FOOTER_RIGHT, default="wifi"): cv.one_of("none", "ip", "wifi", lower=True),
            cv.Optional(CONF_MAX_HEADERS, default=3): cv.int_range(min=1, max=10),
            cv.Optional(CONF_HEADER_ROTATION_INTERVAL, default="5s"): cv.positive_time_period_milliseconds,
            cv.Optional(CONF_ACCENT_DAY, default="fcb712"): color_comp.hex_color,
            cv.Optional(CONF_ACCENT_NIGHT, default="eb1c24"): color_comp.hex_color,
            cv.Optional(CONF_BACKGROUND_COLOR, default="000000"): color_comp.hex_color,
            cv.Optional(CONF_TITLE_COLOR, default="eb1c24"): color_comp.hex_color,
            cv.Optional(CONF_SUBTITLE_COLOR, default="fcb712"): color_comp.hex_color,
            cv.Optional(CONF_DETAIL_COLOR, default="fcb712"): color_comp.hex_color,
        }
    )
    .extend(cv.COMPONENT_SCHEMA)
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    display_var = await cg.get_variable(config[CONF_DISPLAY_ID])
    cg.add(var.set_display(display_var))

    time_var = await cg.get_variable(config[CONF_TIME_ID])
    cg.add(var.set_clock(time_var))

    text_font = await cg.get_variable(config[CONF_TEXT_FONT])
    icon_font = await cg.get_variable(config[CONF_ICON_FONT])
    cg.add(var.set_text_font(text_font))
    cg.add(var.set_icon_font(icon_font))

    cg.add(var.set_max_pages(config[CONF_MAX_PAGES]))
    cg.add(var.set_delimiter(config[CONF_DELIMITER]))
    cg.add(var.set_rotation_interval_ms(config[CONF_ROTATION_INTERVAL].total_milliseconds))
    cg.add(var.set_expiry_interval_ms(config[CONF_EXPIRY_INTERVAL].total_milliseconds))
    cg.add(var.set_update_interval_ms(config[CONF_UPDATE_INTERVAL].total_milliseconds))
    cg.add(var.set_show_weather(config[CONF_SHOW_WEATHER]))
    cg.add(var.set_show_time(config[CONF_SHOW_TIME]))
    cg.add(var.set_show_default_header(config[CONF_SHOW_DEFAULT_HEADER]))
    if CONF_DEFAULT_HEADER_TITLE in config:
        cg.add(var.set_default_header_title(config[CONF_DEFAULT_HEADER_TITLE]))
    if CONF_DEFAULT_HEADER_SUBTITLE in config:
        cg.add(var.set_default_header_subtitle(config[CONF_DEFAULT_HEADER_SUBTITLE]))
    if CONF_TEXT_FONT_LARGE in config:
        text_font_large = await cg.get_variable(config[CONF_TEXT_FONT_LARGE])
        cg.add(var.set_text_font_large(text_font_large))
    if CONF_TIME_ICON_FONT in config:
        time_icon_font = await cg.get_variable(config[CONF_TIME_ICON_FONT])
        cg.add(var.set_time_icon_font(time_icon_font))
    cg.add(var.set_time_format(config[CONF_TIME_FORMAT]))
    cg.add(var.set_date_format(config[CONF_DATE_FORMAT]))
    def as_color(value):
        r, g, b = value
        return cg.RawExpression(f"Color({r}, {g}, {b})")

    cg.add(var.set_accent_day(as_color(config[CONF_ACCENT_DAY])))
    cg.add(var.set_accent_night(as_color(config[CONF_ACCENT_NIGHT])))
    cg.add(var.set_background(as_color(config[CONF_BACKGROUND_COLOR])))
    cg.add(var.set_title_color(as_color(config[CONF_TITLE_COLOR])))
    cg.add(var.set_subtitle_color(as_color(config[CONF_SUBTITLE_COLOR])))
    cg.add(var.set_detail_color(as_color(config[CONF_DETAIL_COLOR])))

    if CONF_WEATHER_STATE in config:
        weather_state = await cg.get_variable(config[CONF_WEATHER_STATE])
        cg.add(var.set_weather_state(weather_state))

    if CONF_SUN_ELEVATION in config:
        sun_elevation = await cg.get_variable(config[CONF_SUN_ELEVATION])
        cg.add(var.set_sun_elevation(sun_elevation))

    if CONF_WIFI_SIGNAL in config:
        wifi_signal = await cg.get_variable(config[CONF_WIFI_SIGNAL])
        cg.add(var.set_wifi_signal(wifi_signal))

    if CONF_WIFI_IP in config:
        wifi_ip = await cg.get_variable(config[CONF_WIFI_IP])
        cg.add(var.set_wifi_ip(wifi_ip))

    footer_map = {"none": 0, "ip": 1, "wifi": 2}
    cg.add(var.set_footer_left(footer_map[config[CONF_FOOTER_LEFT]]))
    cg.add(var.set_footer_right(footer_map[config[CONF_FOOTER_RIGHT]]))
    cg.add(var.set_max_headers(config[CONF_MAX_HEADERS]))
    cg.add(var.set_header_rotation_interval_ms(config[CONF_HEADER_ROTATION_INTERVAL].total_milliseconds))

