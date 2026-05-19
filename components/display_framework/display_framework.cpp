#include "display_framework.h"

#include <cmath>

#include "esphome/core/hal.h"
#include "esphome/core/log.h"

namespace esphome {
namespace display_framework {

static const char *const TAG = "display_framework";

void DisplayFramework::setup() {
  this->slots_.assign(this->max_pages_, {});
  this->current_page_index_ = 0;
  this->headers_.clear();
  this->current_header_index_ = 0;

  this->register_service(
      &DisplayFramework::set_page,
      "set_page",
      {"page_id", "active", "icon", "title", "subtitle", "details", "valid_for_s", "progress", "font_size"});
  this->register_service(&DisplayFramework::set_header, "set_header",
                         {"active", "icon", "title", "subtitle", "valid_for_s", "icon_color", "pulse",
                          "pulse_period_ms", "pulse_min", "pulse_max"});
  this->register_service(&DisplayFramework::set_notification, "set_notification", {"enabled", "icon"});

  if (this->update_interval_ms_ > 0) {
    this->set_interval("update", this->update_interval_ms_, [this]() { this->request_update_(); });
  }
  if (this->rotation_interval_ms_ > 0) {
    this->set_interval("rotate", this->rotation_interval_ms_, [this]() {
      this->rotate_page_();
      this->request_update_();
    });
  }
  if (this->header_rotation_interval_ms_ > 0) {
    this->set_interval("header_rotate", this->header_rotation_interval_ms_, [this]() {
      this->rotate_header_();
      this->request_update_();
    });
  }
  if (this->expiry_interval_ms_ > 0) {
    this->set_interval("expire", this->expiry_interval_ms_, [this]() {
      bool changed = this->expire_pages_();
      uint32_t now_ts = 0;
      if (this->clock_ != nullptr) {
        auto now = this->clock_->now();
        if (now.is_valid()) {
          now_ts = now.timestamp;
        }
      }
      if (this->expire_headers_(now_ts)) {
        changed = true;
      }
      if (changed) {
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

void DisplayFramework::set_page(std::string page_id, bool active, std::string icon, std::string title,
                                std::string subtitle, std::string details, int32_t valid_for_s, int32_t progress,
                                int32_t font_size) {
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
    int normalized_progress = progress;
    if (normalized_progress <= 0) {
      normalized_progress = -1;
    } else if (normalized_progress > 100) {
      normalized_progress = 100;
    }
    int normalized_font_size = (font_size == 1) ? 1 : 0;
    if (index >= 0) {
      ESP_LOGI(TAG, "set_page updating '%s' in slot %d", page_id.c_str(), index);
      auto &slot = this->slots_[index];
      slot.active = true;
      slot.icon = icon;
      slot.title = title;
      slot.subtitle = subtitle;
      slot.details = details;
      slot.progress = normalized_progress;
      slot.font_size = normalized_font_size;
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
      slot.progress = normalized_progress;
      slot.font_size = normalized_font_size;
      slot.expiry_ts = expiry;
    }
  }

  this->refresh_current_page_();
  this->request_update_();
}

void DisplayFramework::set_notification(bool enabled, std::string icon) {
  this->notification_enabled_ = enabled;
  if (!icon.empty()) {
    this->notification_icon_ = icon;
  }
  this->request_update_();
}

void DisplayFramework::set_header(bool active, std::string icon, std::string title, std::string subtitle,
                                  int32_t valid_for_s, std::string icon_color, bool pulse,
                                  int32_t pulse_period_ms, float pulse_min, float pulse_max) {
  uint32_t expiry = 0;
  if (valid_for_s > 0 && this->clock_ != nullptr) {
    auto now = this->clock_->now();
    if (now.is_valid()) {
      expiry = now.timestamp + static_cast<uint32_t>(valid_for_s);
    } else {
      ESP_LOGW(TAG, "set_header: time not valid, expiry disabled");
    }
  }

  if (!active) {
    this->headers_.clear();
    this->current_header_index_ = 0;
    this->request_update_();
    return;
  }

  HeaderSlot slot{};
  slot.active = true;
  slot.icon = icon;
  slot.title = title;
  slot.subtitle = subtitle;
  slot.expiry_ts = expiry;
  slot.pulse_enabled = pulse;
  slot.pulse_period_ms = pulse_period_ms > 0 ? static_cast<uint32_t>(pulse_period_ms) : 1200;
  slot.pulse_min = pulse_min;
  slot.pulse_max = pulse_max;
  if (slot.pulse_min < 0.0f) slot.pulse_min = 0.0f;
  if (slot.pulse_max < 0.0f) slot.pulse_max = 0.0f;
  if (slot.pulse_min > 1.0f) slot.pulse_min = 1.0f;
  if (slot.pulse_max > 1.0f) slot.pulse_max = 1.0f;

  Color parsed_color{};
  if (!icon_color.empty() && this->parse_hex_color_(icon_color, parsed_color)) {
    slot.icon_color_set = true;
    slot.icon_color = parsed_color;
  }

  this->headers_.push_back(slot);
  if (static_cast<int>(this->headers_.size()) > this->max_headers_) {
    this->headers_.erase(this->headers_.begin());
    if (this->current_header_index_ > 0) {
      this->current_header_index_ -= 1;
    }
  }
  this->request_update_();
}

void DisplayFramework::render(display::Display &it) {
  if (this->text_font_ == nullptr || this->icon_font_ == nullptr) {
    ESP_LOGW(TAG, "render skipped: fonts not configured");
    return;
  }

  const int width = it.get_width();
  const int height = it.get_height();
  it.fill(this->background_);

  auto now = this->clock_ != nullptr ? this->clock_->now() : ESPTime();
  bool time_valid = this->clock_ != nullptr && now.is_valid();
  uint32_t now_ts = time_valid ? now.timestamp : 0;

  Color accent_color = this->accent_color_();

  // Dynamic layout
  const int time_height = this->show_time_ ? 22 : 0;
  const bool header_mode = this->has_active_header_();

  int separator_y = -1;
  int dots_y = -1;
  int page_y;
  if (header_mode) {
    separator_y = time_height + 44;
    dots_y = separator_y + 4;
    page_y = dots_y + 10;
  } else {
    page_y = time_height + 6;
  }

  // Time bar
  if (this->show_time_) {
    if (time_valid) {
      it.printf(4, 4, this->text_font_, accent_color, display::TextAlign::TOP_LEFT, "TIME %02d:%02d:%02d", now.hour,
                now.minute, now.second);
      it.printf(width - 4, 4, this->text_font_, accent_color, display::TextAlign::TOP_RIGHT, "%02d-%02d",
                now.day_of_month, now.month);
    } else {
      it.printf(4, 4, this->text_font_, accent_color, display::TextAlign::TOP_LEFT, "TIME --:--");
    }
  }

  // Page dots (header mode only)
  if (header_mode && dots_y >= 0) {
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
      int idx = 0;
      for (int i = 0; i < static_cast<int>(this->slots_.size()); i++) {
        const auto &slot = this->slots_[i];
        if (slot.active && !this->is_expired_(slot, now_ts)) {
          const int x = start_x + (idx * dot_spacing);
          if (i == this->current_page_index_) {
            it.filled_circle(x, dots_y, dot_radius, accent_color);
          } else {
            it.circle(x, dots_y, dot_radius, accent_color);
          }
          idx++;
        }
      }
    }
  }

  // Header and separator
  if (header_mode) {
    int header_text_y = time_height + 6;
    int header_icon_y = time_height - 4;
    if (header_icon_y < 0) header_icon_y = 0;
    this->render_header_(it, now_ts, accent_color, header_text_y, header_icon_y);
    it.filled_rectangle(4, separator_y, width - 8, 1, accent_color);
  }

  // Notification icon
  if (this->notification_enabled_) {
    std::string notif_glyph = this->resolve_icon_glyph_(this->notification_icon_);
    if (!notif_glyph.empty()) {
      it.printf(width - 30, 24, this->icon_font_, accent_color, display::TextAlign::TOP_RIGHT, "%s",
                notif_glyph.c_str());
    }
  }

  // Page content
  const int icon_page_x = 6;
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
    font::Font *page_font = (slot.font_size == 1 && this->text_font_large_ != nullptr)
                                ? this->text_font_large_
                                : this->text_font_;
    std::string page_icon = this->resolve_icon_glyph_(slot.icon);
    bool has_icon = !page_icon.empty();
    const int text_x = has_icon ? 64 : 6;

    if (has_icon) {
      it.printf(icon_page_x, page_y, this->icon_font_, accent_color, display::TextAlign::TOP_LEFT, "%s",
                page_icon.c_str());
    }
    if (!slot.title.empty()) {
      it.printf(text_x, page_y + 2, page_font, this->title_color_, display::TextAlign::TOP_LEFT, "%s",
                slot.title.c_str());
    }
    if (!slot.subtitle.empty()) {
      it.printf(text_x, page_y + 2 + line_height, page_font, this->subtitle_color_,
                display::TextAlign::TOP_LEFT, "%s", slot.subtitle.c_str());
    }
    std::vector<std::string> lines;
    this->split_details_(slot.details, lines);
    for (size_t i = 0; i < lines.size(); i++) {
      it.printf(text_x, page_y + 2 + (line_height * (2 + static_cast<int>(i))), page_font, this->detail_color_,
                display::TextAlign::TOP_LEFT, "%s", lines[i].c_str());
    }
    if (slot.progress > 0) {
      const int bar_width = 140;
      const int bar_height = 10;
      const int bar_x = text_x;
      const int bar_y = page_y + 2 + (line_height * (2 + static_cast<int>(lines.size())));
      this->draw_progress_bar_(it, bar_x, bar_y, bar_width, bar_height, slot.progress, accent_color);
    }
  } else {
    it.printf(6, page_y + 2, this->text_font_, this->detail_color_, display::TextAlign::TOP_LEFT, "NO PAGES");
  }

  this->render_footer_(it, accent_color);
}

bool DisplayFramework::is_expired_(const PageSlot &slot, uint32_t now_ts) const {
  return slot.active && slot.expiry_ts > 0 && now_ts > 0 && now_ts >= slot.expiry_ts;
}

bool DisplayFramework::is_header_expired_(const HeaderSlot &slot, uint32_t now_ts) const {
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

bool DisplayFramework::expire_headers_(uint32_t now_ts) {
  if (this->headers_.empty() || now_ts == 0) {
    return false;
  }
  bool changed = false;
  for (auto it = this->headers_.begin(); it != this->headers_.end();) {
    if (this->is_header_expired_(*it, now_ts)) {
      it = this->headers_.erase(it);
      changed = true;
      if (this->current_header_index_ > 0) {
        this->current_header_index_ -= 1;
      }
    } else {
      ++it;
    }
  }
  if (this->headers_.empty()) {
    this->current_header_index_ = 0;
  } else if (this->current_header_index_ >= static_cast<int>(this->headers_.size())) {
    this->current_header_index_ = 0;
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

bool DisplayFramework::has_active_header_() const {
  if (!this->headers_.empty()) return true;
  return this->show_default_header_;
}

void DisplayFramework::render_header_(display::Display &it, uint32_t now_ts, Color accent_color,
                                      int header_y, int header_icon_y) {
  const int width = it.get_width();
  const int icon_x = width - 52;
  const int icon_y = header_icon_y;
  bool header_active = !this->headers_.empty();
  HeaderSlot *header = nullptr;
  if (header_active) {
    if (this->current_header_index_ >= static_cast<int>(this->headers_.size())) {
      this->current_header_index_ = 0;
    }
    header = &this->headers_[this->current_header_index_];
    if (this->is_header_expired_(*header, now_ts)) {
      this->expire_headers_(now_ts);
      header_active = !this->headers_.empty();
      if (header_active) {
        if (this->current_header_index_ >= static_cast<int>(this->headers_.size())) {
          this->current_header_index_ = 0;
        }
        header = &this->headers_[this->current_header_index_];
      } else {
        header = nullptr;
      }
    }
  }

  Color header_icon_color = (header_active && header != nullptr && header->icon_color_set)
                                ? header->icon_color
                                : accent_color;
  if (header_active && header != nullptr && header->pulse_enabled) {
    header_icon_color = this->apply_pulse_(
        header_icon_color, header->pulse_period_ms, header->pulse_min, header->pulse_max);
  }

  if (header_active) {
    if (header != nullptr && !header->title.empty()) {
      it.printf(4, header_y, this->text_font_, this->title_color_, display::TextAlign::TOP_LEFT, "%s",
                header->title.c_str());
    }
    if (header != nullptr && !header->subtitle.empty()) {
      it.printf(4, header_y + 16, this->text_font_, accent_color, display::TextAlign::TOP_LEFT, "%s",
                header->subtitle.c_str());
    }
    std::string icon = header != nullptr ? this->resolve_icon_glyph_(header->icon) : "";
    if (!icon.empty()) {
      it.printf(icon_x, icon_y, this->icon_font_, header_icon_color, display::TextAlign::TOP_LEFT, "%s",
                icon.c_str());
    }
    return;
  }

  if (this->show_weather_) {
    it.printf(4, header_y, this->text_font_, this->title_color_, display::TextAlign::TOP_LEFT, "WEATHER");

    const char *icon = "\U000F0599";
    if (this->weather_state_ != nullptr && this->weather_state_->has_state()) {
      icon = this->map_weather_icon_(this->weather_state_->state);
    }
    it.printf(icon_x, icon_y, this->icon_font_, header_icon_color, display::TextAlign::TOP_LEFT, "%s", icon);

    std::string weather_label = "unavailable";
    if (this->weather_state_ != nullptr && this->weather_state_->has_state()) {
      weather_label = this->weather_state_->state;
    }
    it.printf(4, header_y + 16, this->text_font_, accent_color, display::TextAlign::TOP_LEFT, "%s",
              weather_label.c_str());
    return;
  }

  if (!this->default_header_title_.empty()) {
    it.printf(4, header_y, this->text_font_, this->title_color_, display::TextAlign::TOP_LEFT, "%s",
              this->default_header_title_.c_str());
    if (!this->default_header_subtitle_.empty()) {
      it.printf(4, header_y + 16, this->text_font_, accent_color, display::TextAlign::TOP_LEFT, "%s",
                this->default_header_subtitle_.c_str());
    }
    return;
  }
  it.printf(4, header_y, this->text_font_, this->title_color_, display::TextAlign::TOP_LEFT, "HAPPY DAY");
  it.printf(4, header_y + 16, this->text_font_, accent_color, display::TextAlign::TOP_LEFT, ":)");
}

void DisplayFramework::rotate_header_() {
  if (this->headers_.size() <= 1) {
    return;
  }
  this->current_header_index_ = (this->current_header_index_ + 1) % static_cast<int>(this->headers_.size());
}

void DisplayFramework::render_footer_(display::Display &it, Color accent_color) {
  const int width = it.get_width();
  const int height = it.get_height();
  const int footer_y = height - 22;

  if (this->footer_left_ == FOOTER_IP) {
    std::string ip_label = "IP --";
    if (this->wifi_ip_ != nullptr && this->wifi_ip_->has_state()) {
      ip_label = "IP " + this->wifi_ip_->state;
    }
    it.printf(4, footer_y, this->text_font_, this->title_color_, display::TextAlign::TOP_LEFT, "%s",
              ip_label.c_str());
  }

  if (this->footer_right_ == FOOTER_WIFI) {
    int bars_x = width - 4 - 18;
    int bars_y = footer_y + 2;
    int level = 0;
    int rssi = 0;
    bool has_rssi = false;
    if (this->wifi_signal_ != nullptr && this->wifi_signal_->has_state()) {
      rssi = static_cast<int>(this->wifi_signal_->state);
      level = this->wifi_level_from_rssi_(this->wifi_signal_->state);
      has_rssi = true;
    }
    this->draw_wifi_bars_(it, bars_x, bars_y, level, accent_color);

    if (has_rssi) {
      it.printf(bars_x - 4, footer_y, this->text_font_, this->title_color_, display::TextAlign::TOP_RIGHT, "RSSI %d",
                rssi);
    } else {
      it.printf(bars_x - 4, footer_y, this->text_font_, this->title_color_, display::TextAlign::TOP_RIGHT, "RSSI --");
    }
  }
}

int DisplayFramework::wifi_level_from_rssi_(float rssi) const {
  if (rssi >= -55.0f) return 4;
  if (rssi >= -67.0f) return 3;
  if (rssi >= -80.0f) return 2;
  if (rssi >= -90.0f) return 1;
  return 0;
}

void DisplayFramework::draw_wifi_bars_(display::Display &it, int x, int y, int level, Color color) {
  const int bar_width = 3;
  const int bar_gap = 2;
  const int max_height = 8;

  for (int i = 0; i < 4; i++) {
    int bar_height = 2 + (i * 2);
    int bar_x = x + (i * (bar_width + bar_gap));
    int bar_y = y + (max_height - bar_height);
    if (level >= (i + 1)) {
      it.filled_rectangle(bar_x, bar_y, bar_width, bar_height, color);
    } else {
      it.rectangle(bar_x, bar_y, bar_width, bar_height, color);
    }
  }
}

void DisplayFramework::draw_progress_bar_(display::Display &it, int x, int y, int width, int height, int progress,
                                          Color color) {
  if (width <= 0 || height <= 0) {
    return;
  }
  int clamped = progress;
  if (clamped < 0) clamped = 0;
  if (clamped > 100) clamped = 100;

  it.rectangle(x, y, width, height, color);
  if (clamped > 0) {
    int fill_width = (width * clamped) / 100;
    int inner_width = fill_width - 2;
    if (inner_width > 0 && height > 2) {
      it.filled_rectangle(x + 1, y + 1, inner_width, height - 2, color);
    }
  }
}

bool DisplayFramework::parse_hex_color_(const std::string &value, Color &out) const {
  std::string hex = value;
  if (hex.empty()) {
    return false;
  }
  if (hex[0] == '#') {
    hex.erase(0, 1);
  }
  if (hex.size() != 6) {
    return false;
  }

  auto hex_to_int = [](char c) -> int {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return 10 + (c - 'a');
    if (c >= 'A' && c <= 'F') return 10 + (c - 'A');
    return -1;
  };

  int r1 = hex_to_int(hex[0]);
  int r2 = hex_to_int(hex[1]);
  int g1 = hex_to_int(hex[2]);
  int g2 = hex_to_int(hex[3]);
  int b1 = hex_to_int(hex[4]);
  int b2 = hex_to_int(hex[5]);
  if (r1 < 0 || r2 < 0 || g1 < 0 || g2 < 0 || b1 < 0 || b2 < 0) {
    return false;
  }

  uint8_t r = static_cast<uint8_t>((r1 << 4) | r2);
  uint8_t g = static_cast<uint8_t>((g1 << 4) | g2);
  uint8_t b = static_cast<uint8_t>((b1 << 4) | b2);
  out = Color(r, g, b);
  return true;
}

Color DisplayFramework::apply_pulse_(Color color, uint32_t period_ms, float min_value, float max_value) const {
  if (period_ms == 0) {
    return color;
  }

  float t = static_cast<float>(millis() % period_ms) / static_cast<float>(period_ms);
  float wave = 0.5f * (1.0f + std::sin(t * 6.2831853f));
  float min_v = std::min(min_value, max_value);
  float max_v = std::max(min_value, max_value);
  float scale = min_v + (max_v - min_v) * wave;

  return this->apply_brightness_(color, scale);
}

Color DisplayFramework::apply_brightness_(Color color, float scale) const {
  scale = std::max(0.0f, std::min(1.0f, scale));
  uint8_t r = static_cast<uint8_t>(color.red * scale);
  uint8_t g = static_cast<uint8_t>(color.green * scale);
  uint8_t b = static_cast<uint8_t>(color.blue * scale);
  return Color(r, g, b);
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
