library(magrittr)
library(dplyr)
library(arrow, warn.conflicts = FALSE)
# make a ggplot line of a single day
library(ggplot2)

# How close is the outdoor air fraction compared to outdoor air damper position signal?
# read parquet
df <-
  read_parquet("../data/coi_bias_-4_annual_clean.parquet") %>%
    mutate(
      time = as.POSIXct(time, format = "%Y-%m-%d %H:%M:%S"),
      oaf_col = (mat_col - rat_col) / (oat_col - rat_col),
      oaf_col = ifelse(oaf_col < 0, NA, ifelse(oaf_col > 1, NA, oaf_col)),
      diff = abs(oat_col - rat_col) < 1,
      date = as.Date(time)
    )


### Minimum outdoor air damper
p <- ggplot() +
  geom_point(data = df %>% filter(slope == 'steady') %>% distinct(),
             aes(y = oaf_col * 100,
                 x = oa_dmpr_sig_col * 100),
             # width = 0.9,
             # height = 0.9,
             show.legend = T, alpha = 0.9) +
  mystyle() +
  theme(legend.position = "top") +

  coord_equal() +
  scale_x_continuous(
    name = "Damper command",
    labels = function(x)
      paste0(x, " %"),
  ) +
  scale_y_continuous(
    name = "Outdoor air fraction",
    labels = function(x)
      paste0(x, " %")
  ) +
  theme(
    panel.grid.major.y = ggplot2::element_line(color = "#cbcbcb"),
    panel.grid.major.x = ggplot2::element_line(color = "#cbcbcb"),
  )
p


df_plot_bands <- df %>%
  filter(date == "2018-08-10") %>%
  select(time, slope)

df_control <- df %>%
  filter(date == "2018-08-10") %>%
  tidyr::pivot_longer(
    cols = c(oa_dmpr_sig_col, cooling_sig_col, heating_sig_col),
    names_to = "variable",
    values_to = "value"
  ) %>%
  mutate(value = value * 100)

ggplot() +
  geom_step(
    data = df_control,
    aes(x = time, y = value, color = variable),
    linewidth = 1,
    show.legend = T
  ) +
  geom_rect(
    data = df_plot_bands,
    aes(
      xmin = time,
      xmax = lead(time),
      ymin = -Inf,
      ymax = Inf,
      fill = slope
    ),
    alpha = 0.2,
    show.legend = F
  ) +
  scale_fill_manual(values = c("transient" = "gray", "steady" = "white")) +  # Customize colors
  mystyle() +
  theme(legend.position = "top") +
  scale_y_continuous(
    name = 'Control signal',
    labels = function(x)
      paste0(x, " %")
  ) +
  scale_x_datetime(date_breaks = "4 hour",
                   date_labels = "%H:%M",
                   expand = c(0, 0))