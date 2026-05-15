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

  void set_page(std::string page_id, bool active, std::string icon, std::string title, std::string subtitle,
                std::string details, int32_t valid_for_s);
  void set_notification(bool enabled, std::string icon);

  void setup() override;
  void dump_config() override;

  void render(display::Display &it);
  void set_update_interval(uint32_t ms) { this->set_update_interval_ms(ms); }

 protected:
  struct PageSlot {
    std::string id;
    bool active{false};
    std::string icon;
    std::string title;
    std::string subtitle;
    std::string details;
    uint32_t expiry_ts{0};
  };

  bool is_expired_(const PageSlot &slot, uint32_t now_ts) const;
  int find_index_(const std::string &page_id) const;
  void clear_slot_(int index);
  void shift_left_from_(int index);
  void rotate_page_();
  bool expire_pages_();
  void refresh_current_page_();
  Color accent_color_() const;
  const char *map_weather_icon_(const std::string &state) const;
  std::string resolve_icon_glyph_(const std::string &icon_name) const;
  void split_details_(const std::string &details, std::vector<std::string> &out) const;
  void request_update_();

  display::Display *display_{nullptr};
  time::RealTimeClock *clock_{nullptr};
  font::Font *text_font_{nullptr};
  font::Font *icon_font_{nullptr};
  text_sensor::TextSensor *weather_state_{nullptr};
  sensor::Sensor *sun_elevation_{nullptr};

  int max_pages_{5};
  std::string delimiter_{"-|-"};
  uint32_t rotation_interval_ms_{20000};
  uint32_t expiry_interval_ms_{10000};
  uint32_t update_interval_ms_{1000};
  bool show_weather_{true};

  Color accent_day_{Color(0xFC, 0xB7, 0x12)};
  Color accent_night_{Color(0xEB, 0x1C, 0x24)};
  Color background_{Color(0, 0, 0)};
  Color title_color_{Color(0xEB, 0x1C, 0x24)};
  Color subtitle_color_{Color(0xFC, 0xB7, 0x12)};
  Color detail_color_{Color(0xFC, 0xB7, 0x12)};

  std::vector<PageSlot> slots_;
  int current_page_index_{0};
  bool notification_enabled_{false};
  std::string notification_icon_{"mdi:bell"};
};

}  // namespace display_framework
}  // namespace esphome
