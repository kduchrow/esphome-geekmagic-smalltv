#include "display_framework.h"

#include "esphome/core/log.h"

namespace esphome {
namespace display_framework {

static const char *const TAG = "display_framework";

void DisplayFramework::setup() {
  this->slots_.assign(this->max_pages_, {});
  this->current_page_index_ = 0;

  if (this->update_interval_ms_ > 0) {
    this->set_interval("update", this->update_interval_ms_, [this]() { this->request_update_(); });
  }
  if (this->rotation_interval_ms_ > 0) {
    this->set_interval("rotate", this->rotation_interval_ms_, [this]() {
      this->rotate_page_();
      this->request_update_();
    });
  }
  if (this->expiry_interval_ms_ > 0) {
    this->set_interval("expire", this->expiry_interval_ms_, [this]() {
      if (this->expire_pages_()) {
        this->request_update_();
      }
    });
  }
}

void DisplayFramework::dump_config() {
  ESP_LOGCONFIG(TAG, "Display Framework:");
  ESP_LOGCONFIG(TAG, "  Max pages: %d", this->max_pages_);
  ESP_LOGCONFIG(TAG, "  Delimiter: '%s'", this->delimiter_.c_str());
  ESP_LOGCONFIG(TAG, "  Rotation interval: %u ms", this->rotation_interval_ms_);
  ESP_LOGCONFIG(TAG, "  Expiry interval: %u ms", this->expiry_interval_ms_);
  ESP_LOGCONFIG(TAG, "  Update interval: %u ms", this->update_interval_ms_);
  ESP_LOGCONFIG(TAG, "  Show weather: %s", this->show_weather_ ? "true" : "false");
  if (this->display_ == nullptr) {
    ESP_LOGW(TAG, "  Display is not set");
  }
  if (this->clock_ == nullptr) {
    ESP_LOGW(TAG, "  Time source is not set");
  }
}

void DisplayFramework::set_page(const std::string &page_id, bool active, const std::string &icon,
                                const std::string &title, const std::string &subtitle, const std::string &details,
                                int32_t valid_for_s) {
  if (page_id.empty()) {
    ESP_LOGW(TAG, "set_page ignored: empty page_id");
    return;
  }

  uint32_t expiry = 0;
  if (valid_for_s > 0 && this->clock_ != nullptr) {
    auto now = this->clock_->now();
    if (now.is_valid()) {
      expiry = now.timestamp + static_cast<uint32_t>(valid_for_s);
    } else {
      ESP_LOGW(TAG, "set_page: time not valid, expiry disabled for '%s'", page_id.c_str());
    }
  }

  int index = this->find_index_(page_id);
  if (!active) {
    if (index >= 0) {
      ESP_LOGI(TAG, "set_page removing '%s'", page_id.c_str());
      this->shift_left_from_(index);
    } else {
      ESP_LOGW(TAG, "set_page remove requested but page not found: '%s'", page_id.c_str());
    }
  } else {
    if (index >= 0) {
      ESP_LOGI(TAG, "set_page updating '%s' in slot %d", page_id.c_str(), index);
      auto &slot = this->slots_[index];
      slot.active = true;
      slot.icon = icon;
      slot.title = title;
      slot.subtitle = subtitle;
      slot.details = details;
      slot.expiry_ts = expiry;
    } else {
      int insert_index = -1;
      for (int i = 0; i < static_cast<int>(this->slots_.size()); i++) {
        if (this->slots_[i].id.empty()) {
          insert_index = i;
          break;
        }
      }
      if (insert_index < 0) {
        ESP_LOGW(TAG, "set_page full, dropping oldest page '%s'", this->slots_[0].id.c_str());
        this->shift_left_from_(0);
        insert_index = static_cast<int>(this->slots_.size()) - 1;
      }
      ESP_LOGI(TAG, "set_page inserting '%s' into slot %d", page_id.c_str(), insert_index);
      auto &slot = this->slots_[insert_index];
      slot.id = page_id;
      slot.active = true;
      slot.icon = icon;
      slot.title = title;
      slot.subtitle = subtitle;
      slot.details = details;
      slot.expiry_ts = expiry;
    }
  }

  this->refresh_current_page_();
  this->request_update_();
}

void DisplayFramework::set_notification(bool enabled, const std::string &icon) {
  this->notification_enabled_ = enabled;
  if (!icon.empty()) {
    this->notification_icon_ = icon;
  }
  this->request_update_();
}

void DisplayFramework::render(display::DisplayBuffer &it) {
  if (this->text_font_ == nullptr || this->icon_font_ == nullptr) {
    ESP_LOGW(TAG, "render skipped: fonts not configured");
    return;
  }

  const int width = it.get_width();
  const int height = it.get_height();
  it.fill(this->background_);

  auto now = this->clock_ != nullptr ? this->clock_->now() : time::ESPTime();
  bool time_valid = this->clock_ != nullptr && now.is_valid();

  Color accent_color = this->accent_color_();

  if (time_valid) {
    it.printf(4, 4, this->text_font_, accent_color, display::TextAlign::TOP_LEFT, "TIME %02d:%02d:%02d", now.hour,
              now.minute, now.second);
    it.printf(width - 4, 4, this->text_font_, accent_color, display::TextAlign::TOP_RIGHT, "%02d-%02d",
              now.day_of_month, now.month);
  } else {
    it.printf(4, 4, this->text_font_, accent_color, display::TextAlign::TOP_LEFT, "TIME --:--");
  }

  uint32_t now_ts = (time_valid) ? now.timestamp : 0;

  int active_count = 0;
  for (const auto &slot : this->slots_) {
    if (slot.active && !this->is_expired_(slot, now_ts)) {
      active_count++;
    }
  }
  if (active_count > 0) {
    const int dot_spacing = 8;
    const int dot_radius = 2;
    const int dots_width = (active_count - 1) * dot_spacing;
    const int start_x = (width / 2) - (dots_width / 2);
    const int dot_y = 70;
    int idx = 0;
    for (int i = 0; i < static_cast<int>(this->slots_.size()); i++) {
      const auto &slot = this->slots_[i];
      if (slot.active && !this->is_expired_(slot, now_ts)) {
        const int x = start_x + (idx * dot_spacing);
        if (i == this->current_page_index_) {
          it.filled_circle(x, dot_y, dot_radius, accent_color);
        } else {
          it.circle(x, dot_y, dot_radius, accent_color);
        }
        idx++;
      }
    }
  }

  if (this->show_weather_) {
    int y = 28;
    it.printf(4, y, this->text_font_, this->title_color_, display::TextAlign::TOP_LEFT, "WEATHER");

    const int icon_x = width - 52;
    const int icon_y = 18;
    const char *icon = "\U000F0599";
    if (this->weather_state_ != nullptr && this->weather_state_->has_state()) {
      icon = this->map_weather_icon_(this->weather_state_->state);
    }
    it.printf(icon_x, icon_y, this->icon_font_, accent_color, display::TextAlign::TOP_LEFT, "%s", icon);
    y += 16;

    std::string weather_label = "unavailable";
    if (this->weather_state_ != nullptr && this->weather_state_->has_state()) {
      weather_label = this->weather_state_->state;
    }
    it.printf(4, y, this->text_font_, accent_color, display::TextAlign::TOP_LEFT, "%s", weather_label.c_str());
  }

  it.filled_rectangle(4, 66, width - 8, 1, accent_color);

  if (this->notification_enabled_) {
    std::string notif_glyph = this->resolve_icon_glyph_(this->notification_icon_);
    if (!notif_glyph.empty()) {
      it.printf(width - 30, 24, this->icon_font_, accent_color, display::TextAlign::TOP_RIGHT, "%s",
                notif_glyph.c_str());
    }
  }

  const int page_y = 82;
  const int icon_page_x = 6;
  const int text_x = 64;
  const int line_height = 18;

  int page_index = this->current_page_index_;
  if (page_index < 0 || page_index >= static_cast<int>(this->slots_.size()) ||
      !this->slots_[page_index].active || this->is_expired_(this->slots_[page_index], now_ts)) {
    page_index = -1;
    for (int i = 0; i < static_cast<int>(this->slots_.size()); i++) {
      if (this->slots_[i].active && !this->is_expired_(this->slots_[i], now_ts)) {
        page_index = i;
        break;
      }
    }
  }

  if (page_index >= 0) {
    const auto &slot = this->slots_[page_index];
    std::string page_icon = this->resolve_icon_glyph_(slot.icon);
    if (!page_icon.empty()) {
      it.printf(icon_page_x, page_y, this->icon_font_, accent_color, display::TextAlign::TOP_LEFT, "%s",
                page_icon.c_str());
    }

    if (!slot.title.empty()) {
      it.printf(text_x, page_y + 2, this->text_font_, this->title_color_, display::TextAlign::TOP_LEFT, "%s",
                slot.title.c_str());
    }
    if (!slot.subtitle.empty()) {
      it.printf(text_x, page_y + 2 + line_height, this->text_font_, this->subtitle_color_,
                display::TextAlign::TOP_LEFT, "%s", slot.subtitle.c_str());
    }

    std::vector<std::string> lines;
    this->split_details_(slot.details, lines);
    for (size_t i = 0; i < lines.size(); i++) {
      it.printf(text_x, page_y + 2 + (line_height * (2 + static_cast<int>(i))), this->text_font_, this->detail_color_,
                display::TextAlign::TOP_LEFT, "%s", lines[i].c_str());
    }
  } else {
    it.printf(text_x, page_y + 2, this->text_font_, this->detail_color_, display::TextAlign::TOP_LEFT, "NO PAGES");
  }
}

bool DisplayFramework::is_expired_(const PageSlot &slot, uint32_t now_ts) const {
  return slot.active && slot.expiry_ts > 0 && now_ts > 0 && now_ts >= slot.expiry_ts;
}

int DisplayFramework::find_index_(const std::string &page_id) const {
  if (page_id.empty()) {
    return -1;
  }
  for (int i = 0; i < static_cast<int>(this->slots_.size()); i++) {
    if (this->slots_[i].id == page_id) {
      return i;
    }
  }
  return -1;
}

void DisplayFramework::clear_slot_(int index) {
  if (index < 0 || index >= static_cast<int>(this->slots_.size())) {
    return;
  }
  this->slots_[index] = PageSlot{};
}

void DisplayFramework::shift_left_from_(int index) {
  if (index < 0 || index >= static_cast<int>(this->slots_.size())) {
    return;
  }
  for (int i = index; i < static_cast<int>(this->slots_.size()) - 1; i++) {
    this->slots_[i] = this->slots_[i + 1];
  }
  this->clear_slot_(static_cast<int>(this->slots_.size()) - 1);
}

void DisplayFramework::rotate_page_() {
  if (this->slots_.empty()) {
    return;
  }

  uint32_t now_ts = 0;
  if (this->clock_ != nullptr) {
    auto now = this->clock_->now();
    if (now.is_valid()) {
      now_ts = now.timestamp;
    }
  }

  int current = this->current_page_index_;
  int next = -1;
  for (int offset = 1; offset <= static_cast<int>(this->slots_.size()); offset++) {
    int i = (current + offset) % static_cast<int>(this->slots_.size());
    if (this->slots_[i].active && !this->is_expired_(this->slots_[i], now_ts)) {
      next = i;
      break;
    }
  }
  if (next >= 0) {
    this->current_page_index_ = next;
  }
}

bool DisplayFramework::expire_pages_() {
  if (this->clock_ == nullptr) {
    return false;
  }
  auto now = this->clock_->now();
  if (!now.is_valid()) {
    return false;
  }
  uint32_t ts = now.timestamp;
  bool changed = false;
  for (int i = 0; i < static_cast<int>(this->slots_.size()); i++) {
    if (this->slots_[i].active && this->is_expired_(this->slots_[i], ts)) {
      ESP_LOGI(TAG, "page expired, removing '%s'", this->slots_[i].id.c_str());
      this->shift_left_from_(i);
      i -= 1;
      changed = true;
    }
  }
  if (changed) {
    this->refresh_current_page_();
  }
  return changed;
}

void DisplayFramework::refresh_current_page_() {
  if (this->slots_.empty()) {
    this->current_page_index_ = 0;
    return;
  }

  uint32_t now_ts = 0;
  if (this->clock_ != nullptr) {
    auto now = this->clock_->now();
    if (now.is_valid()) {
      now_ts = now.timestamp;
    }
  }

  if (this->current_page_index_ < 0 || this->current_page_index_ >= static_cast<int>(this->slots_.size()) ||
      !this->slots_[this->current_page_index_].active ||
      this->is_expired_(this->slots_[this->current_page_index_], now_ts)) {
    int next = -1;
    for (int i = 0; i < static_cast<int>(this->slots_.size()); i++) {
      if (this->slots_[i].active && !this->is_expired_(this->slots_[i], now_ts)) {
        next = i;
        break;
      }
    }
    this->current_page_index_ = (next >= 0) ? next : 0;
  }
}

Color DisplayFramework::accent_color_() const {
  bool is_day = true;
  if (this->sun_elevation_ != nullptr && this->sun_elevation_->has_state()) {
    is_day = this->sun_elevation_->state > 0.0f;
  }
  return is_day ? this->accent_day_ : this->accent_night_;
}

const char *DisplayFramework::map_weather_icon_(const std::string &state) const {
  if (state == "clear-night") return "\U000F0594";
  if (state == "cloudy") return "\U000F0590";
  if (state == "exceptional") return "\U000F0026";
  if (state == "fog") return "\U000F0591";
  if (state == "hail") return "\U000F0592";
  if (state == "lightning") return "\U000F0593";
  if (state == "lightning-rainy") return "\U000F067E";
  if (state == "partlycloudy") return "\U000F0595";
  if (state == "pouring") return "\U000F0596";
  if (state == "rainy") return "\U000F0597";
  if (state == "snowy") return "\U000F0598";
  if (state == "snowy-rainy") return "\U000F067F";
  if (state == "sunny") return "\U000F0599";
  if (state == "windy") return "\U000F059D";
  if (state == "windy-variant") return "\U000F059E";
  return "\U000F0599";
}

std::string DisplayFramework::resolve_icon_glyph_(const std::string &icon_name) const {
  if (icon_name.empty()) {
    return "";
  }
  if (icon_name.rfind("mdi:", 0) != 0) {
    return icon_name;
  }

  if (icon_name == "mdi:solar-power") return "\U000F0A72";
  if (icon_name == "mdi:battery") return "\U000F0079";
  if (icon_name == "mdi:battery-charging") return "\U000F0084";
  if (icon_name == "mdi:flash") return "\U000F0241";
  if (icon_name == "mdi:lightning-bolt") return "\U000F140B";
  if (icon_name == "mdi:home") return "\U000F02DC";
  if (icon_name == "mdi:weather-sunny") return "\U000F0599";
  if (icon_name == "mdi:weather-cloudy") return "\U000F0590";
  if (icon_name == "mdi:weather-rainy") return "\U000F0597";
  if (icon_name == "mdi:weather-partly-cloudy") return "\U000F0595";
  if (icon_name == "mdi:weather-windy") return "\U000F059D";
  if (icon_name == "mdi:bell") return "\U000F009A";
  if (icon_name == "mdi:bell-ring") return "\U000F009F";

  return "\U000F0026";
}

void DisplayFramework::split_details_(const std::string &details, std::vector<std::string> &out) const {
  out.clear();
  if (details.empty()) {
    return;
  }

  std::string delimiter = this->delimiter_;
  if (delimiter.empty()) {
    delimiter = "-|-";
  }

  size_t pos = 0;
  while (out.size() < 4) {
    size_t next = details.find(delimiter, pos);
    std::string part;
    if (next == std::string::npos) {
      part = details.substr(pos);
    } else {
      part = details.substr(pos, next - pos);
    }

    if (!part.empty()) {
      out.push_back(part);
    }

    if (next == std::string::npos) {
      break;
    }
    pos = next + delimiter.size();
  }
}

void DisplayFramework::request_update_() {
  if (this->display_ != nullptr) {
    this->display_->update();
  }
}

}  // namespace display_framework
}  // namespace esphome
