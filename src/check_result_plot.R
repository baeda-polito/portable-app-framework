library(formattable)
library(magrittr)
library(tidyr)
library(dplyr)
# load results
df <- read.csv("data/result.csv",) %>%

  colnames(df) <- c("dataset", "rm", "check1", "check2", "check3", "check4", "check5")

df <- select(df, -rm)
df_plot <- df %>%
  tidyr::pivot_longer(
    cols = c("check1", "check2", "check3", "check4", "check5"),
    names_to = "variable",
    values_to = "value"
  ) %>%
  mutate(value = as.factor(as.character(value)))


library(ggplot2)

# assign text colour
textcol <- "grey40"

ggplot(df_plot) +
  geom_tile(aes(y = dataset, x = variable, fill = value), colour = "white", size = 0.25) +
  scale_fill_manual(values = c("#d53e4f", "#f46d43", "#fdae61", "#fee08b", "#e6f598", "#abdda4", "#ddf1da"), na.value = "grey90") +
  # coord_fixed() +
  labs(x = "", y = "", title = "Precheck results") +
  scale_y_discrete(expand = c(0, 0)) +
  scale_x_discrete(expand = c(0, 0)) +
  theme_grey(base_size = 20) +
  theme(legend.position = "right", legend.direction = "vertical",
        legend.title = element_text(colour = textcol),
        legend.margin = margin(grid::unit(0, "cm")),
        legend.text = element_text(colour = textcol, vjust = 0.2, face = "bold"),
        legend.key.height = grid::unit(0.8, "cm"),
        legend.key.width = grid::unit(0.2, "cm"),
        axis.text.x = element_text(vjust = 0.2, colour = textcol),
        axis.text.y = element_text(vjust = 0.2, colour = textcol),
        axis.ticks = element_line(size = 0.4),
        plot.background = element_blank(),
        panel.border = element_blank(),
        plot.margin = margin(0.7, 0.4, 0.1, 0.2, "cm"),
        plot.title = element_text(colour = textcol, hjust = 0, vjust = 0.2, face = "bold")
  )

ggsave("data/result.png", width = 10, height = 10, dpi = 300)


# install.packages("remotes")
# remotes::install_github("davidsjoberg/ggsankey")
library(ggsankey)


t1 <- sample(x = c("AHU", "DDAHU"), size = 100, replace = TRUE)
t2 <- sample(x = c("Failed", "Passed"), size = 100, replace = TRUE)
t3 <- sample(x = c("Failed", "Passed"), size = 100, replace = TRUE)

d <- data.frame(cbind(t1, t2, t3))
names(d) <- c('Dataset', 'Check1', 'Check2')

head(d)

# Step 1
df <- d %>%
  make_long(Dataset, Check1, Check2)
df

ggplot(df, aes(x = x,
               next_x = next_x,
               node = node,
               next_node = next_node,
               fill = factor(node),
               label = node)
) +
  geom_sankey(flow.alpha = 0.5,
              node.color = "black",
              show.legend = FALSE) +
  geom_sankey_label(size = 3, color = "black", fill = "white", hjust = -0.5) +
  theme_void() +
  theme(legend.position = "none") +
  theme(axis.title = element_blank(),
        axis.text.y = element_blank(),
        axis.ticks = element_blank(),
        panel.grid = element_blank()) +
  scale_fill_viridis_d(option = "inferno")


