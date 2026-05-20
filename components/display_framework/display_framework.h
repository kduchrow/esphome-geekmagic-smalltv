#pragma once

#include <string>
#include <vector>

#include "esphome/core/component.h"
#include "esphome/core/color.h"
#include "esphome/components/display/display.h"
#include "esphome/components/font/font.h"
#include "esphome/components/api/custom_api_device.h"
#include "esphome/components/time/real_time_clock.h"
#include "esphome/components/text_sensor/text_sensor.h"
#include "esphome/components/sensor/sensor.h"

namespace esphome {
namespace display_framework {

class DisplayFramework : public Component, public api::CustomAPIDevice {
 public:
  void set_display(display::Display *display) { this->display_ = display; }
  void set_clock(time::RealTimeClock *clock) { this->clock_ = clock; }
  void set_text_font(font::Font *font) { this->text_font_ = font; }
  void set_icon_font(font::Font *font) { this->icon_font_ = font; }
  void set_weather_state(text_sensor::TextSensor *sensor) { this->weather_state_ = sensor; }
  void set_sun_elevation(sensor::Sensor *sensor) { this->sun_elevation_ = sensor; }
  void set_wifi_ip(text_sensor::TextSensor *sensor) { this->wifi_ip_ = sensor; }
  void set_wifi_signal(sensor::Sensor *sensor) { this->wifi_signal_ = sensor; }
  void set_max_pages(int max_pages) { this->max_pages_ = max_pages; }
  void set_delimiter(const std::string &delimiter) { this->delimiter_ = delimiter; }
  void set_rotation_interval_ms(uint32_t ms) { this->rotation_interval_ms_ = ms; }
  void set_expiry_interval_ms(uint32_t ms) { this->expiry_interval_ms_ = ms; }
  void set_update_interval_ms(uint32_t ms) { this->update_interval_ms_ = ms; }
  void set_show_weather(bool show_weather) { this->show_weather_ = show_weather; }
  void set_accent_day(Color color) { this->accent_day_ = color; }
  void set_accent_night(Color color) { this->accent_night_ = color; }
  void set_background(Color color) { this->background_ = color; }
  void set_title_color(Color color) { this->title_color_ = color; }
  void set_subtitle_color(Color color) { this->subtitle_color_ = color; }
  void set_detail_color(Color color) { this->detail_color_ = color; }
  void set_footer_left(int mode) { this->footer_left_ = mode; }
  void set_footer_right(int mode) { this->footer_right_ = mode; }
  void set_max_headers(int max_headers) { this->max_headers_ = max_headers; }
  void set_header_rotation_interval_ms(uint32_t ms) { this->header_rotation_interval_ms_ = ms; }
  void set_show_time(bool v) { this->show_time_ = v; }
  void set_show_default_header(bool v) { this->show_default_header_ = v; }
  void set_default_header_title(const std::string &v) { this->default_header_title_ = v; }
  void set_default_header_subtitle(const std::string &v) { this->default_header_subtitle_ = v; }
  void set_text_font_large(font::Font *f) { this->text_font_large_ = f; }
  void set_time_icon_font(font::Font *f) { this->time_icon_font_ = f; }
  void set_time_format(const std::string &fmt) { this->time_format_ = fmt; }
  void set_date_format(const std::string &fmt) { this->date_format_ = fmt; }

  void set_page(std::string page_id, bool active, std::string icon, std::string title, std::string subtitle,
                std::string details, int32_t valid_for_s, int32_t progress, int32_t font_size);
  void set_header(bool active, std::string icon, std::string title, std::string subtitle, int32_t valid_for_s,
                  std::string icon_color, bool pulse, int32_t pulse_period_ms, float pulse_min, float pulse_max);
  void set_notification(bool enabled, std::string icon);

  void setup() override;
  void dump_config() override;

  void render(display::Display &it);
  void set_update_interval(uint32_t ms) { this->set_update_interval_ms(ms); }

 protected:
  static constexpr int FOOTER_NONE = 0;
  static constexpr int FOOTER_IP = 1;
  static constexpr int FOOTER_WIFI = 2;

  struct PageSlot {
    std::string id;
    bool active{false};
    std::string icon;
    std::string title;
    std::string subtitle;
    std::string details;
    int progress{-1};
    int font_size{0};
    uint32_t expiry_ts{0};
  };

  struct HeaderSlot {
    bool active{false};
    std::string icon;
    std::string title;
    std::string subtitle;
    uint32_t expiry_ts{0};
    bool icon_color_set{false};
    Color icon_color{Color(0, 0, 0)};
    bool pulse_enabled{false};
    uint32_t pulse_period_ms{1200};
    float pulse_min{0.4f};
    float pulse_max{1.0f};
  };

  bool is_expired_(const PageSlot &slot, uint32_t now_ts) const;
  bool is_header_expired_(const HeaderSlot &slot, uint32_t now_ts) const;
  int find_index_(const std::string &page_id) const;
  void clear_slot_(int index);
  void shift_left_from_(int index);
  void rotate_page_();
  bool expire_pages_();
  bool expire_headers_(uint32_t now_ts);
  void refresh_current_page_();
  void rotate_header_();
  bool has_active_header_() const;
  void render_header_(display::Display &it, uint32_t now_ts, Color accent_color, int header_text_y, int header_icon_y);
  void render_footer_(display::Display &it, Color accent_color);
  int wifi_level_from_rssi_(float rssi) const;
  void draw_wifi_bars_(display::Display &it, int x, int y, int level, Color color);
  void draw_progress_bar_(display::Display &it, int x, int y, int width, int height, int progress, Color color);
  bool parse_hex_color_(const std::string &value, Color &out) const;
  Color apply_pulse_(Color color, uint32_t period_ms, float min_value, float max_value) const;
  Color apply_brightness_(Color color, float scale) const;
  Color accent_color_() const;
  const char *map_weather_icon_(const std::string &state) const;
  std::string resolve_icon_glyph_(const std::string &icon_name) const;
  void split_details_(const std::string &details, std::vector<std::string> &out) const;
  std::vector<std::string> wrap_text_(const std::string &text, font::Font *font, int max_width) const;
  void request_update_();

  display::Display *display_{nullptr};
  time::RealTimeClock *clock_{nullptr};
  font::Font *text_font_{nullptr};
  font::Font *icon_font_{nullptr};
  text_sensor::TextSensor *weather_state_{nullptr};
  sensor::Sensor *sun_elevation_{nullptr};
  text_sensor::TextSensor *wifi_ip_{nullptr};
  sensor::Sensor *wifi_signal_{nullptr};

  int max_pages_{5};
  int max_headers_{3};
  std::string delimiter_{"-|-"};
  uint32_t rotation_interval_ms_{20000};
  uint32_t expiry_interval_ms_{10000};
  uint32_t update_interval_ms_{1000};
  uint32_t header_rotation_interval_ms_{5000};
  bool show_weather_{true};
  bool show_time_{true};
  bool show_default_header_{true};
  std::string default_header_title_{};
  std::string default_header_subtitle_{};
  font::Font *text_font_large_{nullptr};
  font::Font *time_icon_font_{nullptr};
  std::string time_format_{"%H:%M:%S"};
  std::string date_format_{"%d.%m"};

  Color accent_day_{Color(0xFC, 0xB7, 0x12)};
  Color accent_night_{Color(0xEB, 0x1C, 0x24)};
  Color background_{Color(0, 0, 0)};
  Color title_color_{Color(0xEB, 0x1C, 0x24)};
  Color subtitle_color_{Color(0xFC, 0xB7, 0x12)};
  Color detail_color_{Color(0xFC, 0xB7, 0x12)};
  int footer_left_{FOOTER_IP};
  int footer_right_{FOOTER_WIFI};

  std::vector<PageSlot> slots_;
  std::vector<HeaderSlot> headers_{};
  int current_header_index_{0};
  int current_page_index_{0};
  bool notification_enabled_{false};
  std::string notification_icon_{"mdi:bell"};
};

}  // namespace display_framework
}  // namespace esphome
