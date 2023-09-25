library(magrittr)
library(dplyr)
# How close is the outdoor air fraction compared to outdoor air damper position signal?
# read csv
df <- read.csv("data/LBNL_FDD_Dataset_SDAHU/damper_stuck_100_annual_short.csv")

df <- df[1:1000,]
# convert to posixct time
df$timestamp <- as.POSIXct(df$Datetime, format = "%Y-%m-%d %H:%M:%S")
# resample to 15 min and calculate mean
df<-df %>%
  mutate(timestamp = as.POSIXct(timestamp)) %>%
  group_by(timestamp = cut(timestamp, breaks = "15 min")) %>%
  summarise(OA_TEMP = mean(OA_TEMP, na.rm = T),
            MA_TEMP = mean(MA_TEMP, na.rm = T),
            RA_TEMP = mean(RA_TEMP, na.rm = T),
            OA_DMPR_DM = mean(OA_DMPR_DM, na.rm = T)) %>%
  mutate(timestamp = as.POSIXct(timestamp, format = "%Y-%m-%d %H:%M:%S"))
  
# make a ggplot line of a single day
library(ggplot2)


ggplot(mpg, aes(displ, hwy)) + 
  geom_point() + 
  scale_y_continuous(
    "mpg (US)", 
    sec.axis = sec_axis(~ . * 1.20, name = "mpg (UK)")
  )
scalefactor = 0.01

ggplot(df, linewidth = 2) +
  geom_line(aes(x = timestamp, y = OA_TEMP), linewidth = 2, color = "blue", show.legend = T) +
  geom_line(aes(x = timestamp, y = MA_TEMP), linewidth = 2,color = "green") +
  geom_line(aes(x = timestamp, y = RA_TEMP), linewidth = 2,color = "orange") +
  geom_line(aes(x = timestamp, y = OA_DMPR_DM/scalefactor),linewidth = 2, color = "red") +
  
  geom_line(aes(x = timestamp, y = OA_DMPR_DM/scalefactor),linewidth = 2, color = "red") +
  scale_x_datetime(date_breaks = "1 hour", date_labels = "%H:%M") +
  scale_y_continuous("Temperature [°C]", sec.axis = sec_axis(~.*scalefactor, name = "Command [-]")) 
