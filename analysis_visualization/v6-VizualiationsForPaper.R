#####
# This R File generates all of the visualizations in the paper.
# Relies on a data.csv file for accuracy visualization
# Relies on a factuality.excel file for Factuality visualization.
#####


# Load required packages
library(ggplot2)
library(dplyr)
library(tidyr)
library(readxl)


# Read the CSV file
data <- read.csv("data/data.csv")
# Set Data columns as factors and levels
data$audience <- factor(data$audience)
data$example <- factor(data$example)
data$person <- factor(data$person)
data$ground_truth <- factor(data$ground_truth)

levels(data$audience) <- c("No Audience", "Self", "Peer", "Manager")
levels(data$example) <- c("0-Shot (none)", "1-Shot (manual)", "Masked Manual", "Masked Template")
levels(data$person) <- c("P1", "P2", "P3")
levels(data$ground_truth) <- c("Manual", "Baseline", "Additional")


folder <- "figs/v6/"


#####
# All accuracy measures in one graph
####

gathered_metrics <- data %>%
  gather(key = "metric", value = "Score", rouge, bleu, bleurt, ter) %>%
  mutate(Audience = audience) %>%
  select(-audience) %>%
  mutate(Prompting = example) %>%
  select(-example) %>%
  select(-word_count, -character_count)

gathered_metrics$metric <- factor(gathered_metrics$metric)
levels(gathered_metrics$metric) <- c("ROUGE", "BLEU", "BLEURT", "TER")

gathered_metrics %>%
  ggplot(aes(x = ground_truth, y = Score, fill = Audience)) +
  geom_boxplot() +
  facet_wrap(~metric, scales = "free") +
  labs(title = "Accuracy Measures by Audience")

gathered_metrics %>%
  ggplot(aes(x = ground_truth, y = Score, fill = Prompting)) +
  geom_boxplot() +
  facet_wrap(~metric, scales = "free") +
  labs(title = "Accuracy Measures by Example")


gathered_metrics %>%
  ggplot(aes(x = ground_truth, y = Score, fill = Audience)) +
  geom_boxplot() +
  facet_grid(metric ~ Prompting, scales = "free") +
  labs(title = "Accuracy Measures by Audience and Example")

# Put both Accuracy and Example in the same figure
gathered_metrics2 <- gathered_metrics %>%
  gather(key = "key_factor", value = "Experiment Level", Audience, Prompting)
# Reorder the levels of the 'category' factor

levels(gathered_metrics2$`Experiment Level`) <- c("No Audience", "Self", "Peer", "Manager", "0-Shot (none)", "1-Shot (manual)", "Masked Manual", "Masked Template")
gathered_metrics2$`Experiment Level` <- factor(gathered_metrics2$`Experiment Level`, levels = c("No Audience", "Self", "Peer", "Manager", "0-Shot (none)", "1-Shot (manual)", "Masked Manual", "Masked Template"))
gathered_metrics2 %>%
  ggplot(aes(x = ground_truth, y = Score, fill = `Experiment Level`)) +
  geom_boxplot(color = "#888888") +
  facet_wrap(key_factor ~ metric, nrow = 2, ncol = 4, scales = "free") +
  scale_fill_manual(values = c("#ffffcc", "#c2e699", "#78c679", "#238443", "#feebe2", "#fbb4b9", "#f768a1", "#ae017e")) +
  labs(title = "Accuracy Measures by Audience Type and Prompt Engineering Approach", x = "Ground Truth Comparison")
ggsave(paste0(folder, "accuracyMeasures.png"), height = 10, width = 22)
ggsave(paste0(folder, "accuracyMeasures.pdf"), height = 10, width = 22)


#####
#Stacked bar chart for Factuality Errors
####

factuality <- read_excel("data/calculatingFactuality.xlsx", sheet = 1)
# check the imported data shape
# print(factuality)

factuality <- factuality %>%
  mutate(`Repeated Phrase` = `Other Errors`) %>%
  select(
    `Participant Number`,
    `Repeated Phrase`,
    `Content Verifiability Errors`,
    `Discourse Errors`,
    `Semantic Frame Errors`
  )

# Convert the "Participant Number" column to a factor with custom levels and labels
# Also modify ordering for plotting.
factuality$participant <- factor(factuality$`Participant Number`,
                                        levels = c(3, 2, 1),
                                        labels = c("Session 3", "Session 2", "Session 1"))
# Drop extra column before melting data
factuality <- factuality %>%
  select(-`Participant Number`)

# Melt the data frame to long format
fact_long <- reshape2::melt(factuality, id.vars = "participant") %>%
  mutate("Error Type" = variable)

# check the data shape is long now
# print(fact_long)

# Create the stacked bar charts
ggplot(fact_long, aes(x = value, y = participant, fill = `Error Type`)) +
  geom_bar(stat = "identity") +
  labs(title = "Factuality Errors by Participant Baseline Summary",
       x = "Percentage of Factuality Errors Present in Baseline Summary",
       y = NULL) +
  scale_fill_manual(values = c("#92c5de", "#0571b0", "#f4a582", "#ca0020")) +
  scale_x_continuous(labels = scales::percent_format(value = 1),
                     limits = c(0, 1)) +
  theme_minimal() +
  theme(legend.position = c(0.75, 0.5)) +
  theme(
    legend.background = element_rect(fill = "#eeeeee", color = "#888888"),
    panel.grid.major.x = element_line(color = "#888888"),
    panel.grid.major.y = element_blank(),
    panel.grid.minor = element_line(color = "#aaaaaa")
  )
ggsave(paste0(folder, "factuality.png"), width = 6, height = 3)
ggsave(paste0(folder, "factuality.pdf"), width = 6, height = 3)
