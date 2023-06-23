# Load required packages
library(ggplot2)
library(dplyr)
library(tidyr)

# Read the CSV file
data <- read.csv("data/data.csv")
# Set Data columns as factors and levels
data$audience <- factor(data$audience)
data$example <- factor(data$example)
data$person <- factor(data$person)
data$ground_truth <- factor(data$ground_truth)

levels(data$audience) <- c("None", "Self", "Peer", "Manager")
levels(data$example) <- c("None", "Manual", "Man.Masked", "Temp.Masked")
levels(data$person) <- c("P1","P2","P3")
levels(data$ground_truth) <- c("Manual", "Baseline", "Additional")


folder = "figs/v6/"
personFilter = 1


#Groups the metrics into a single column
# data %>%
#   gather(key = "metric", value = "value", word_count, rouge, bleu, bleurt, ter)

data %>%
  # filter(person == personFilter) %>% # & entity_type == "TOTAL") %>%
  # summary()
  ggplot( aes(x = example, y = word_count, fill = example)) +
  geom_boxplot()
  # facet_wrap(~audience, scales = "fixed")
  # labs(title = paste0("Entities by Audience for Paricipant",personFilter), x = "Audience", y = "Counts Over Summary Length")
  



#Show all accuracy measures in one graph
gatheredMetrics <- data %>%
  gather(key = "metric", value = "Score", rouge, bleu, bleurt, ter) %>%
  mutate(Audience = audience) %>%
  select(-audience) %>%
  mutate(Example = example) %>%
  select(-example)
    
gatheredMetrics$metric <- factor(gatheredMetrics$metric)
levels(gatheredMetrics$metric) <- c("ROUGE", "BLEU", "BLEURT", "TER")
    
gatheredMetrics %>%
  ggplot(aes(x = ground_truth, y = Score, fill = Audience)) + 
  geom_boxplot() +
  facet_wrap(~metric, scales = "free") + 
  labs(title = "Accuracy Measures by Audience")
  
gatheredMetrics %>%
  ggplot(aes(x = ground_truth, y = Score, fill = Example)) + 
  geom_boxplot() +
  facet_wrap(~metric, scales = "free") + 
  labs(title = "Accuracy Measures by Example")


gatheredMetrics %>%
  ggplot(aes(x = ground_truth, y = Score, fill = Audience)) + 
  geom_boxplot() +
  facet_grid(Example ~ metric, scales = "free") + 
  labs(title = "Accuracy Measures by Audience and Example")

# Put both Accuracy and Example in the same figure
gatheredMetrics2 <- gatheredMetrics%>%
  gather(key = "key_factor", value = "Level", Audience, Example )

gatheredMetrics2 %>%
  ggplot(aes(x = ground_truth, y = Score, fill = Level)) + 
  geom_boxplot() +
  facet_wrap(key_factor ~ metric, nrow = 2, ncol = 4, scales = "free") + 
  labs(title = "Accuracy Measures by Audience and Example")
ggsave(paste0(folder,"accuracyMeasures.png"))


#Stacked bar chart for Factuality Errors

# Create the data frame
factuality <- data.frame(
  Participant = c("Session 1", "Session 2", "Session 3"),
  "Other Errors" = c(7.39, 2.86, 6.06),
  "Content Verifiability Errors" = c(1.48, 6.67, 6.06),
  "Discourse Errors" = c(0.00, 0.95, 1.01),
  "Semantic Frame Errors" = c(0.00, 0.00, 0.00)
  )#, No_Errors = c(91.13, 89.52, 86.87))

factuality$Participant <- factor(factuality$Participant, levels = rev(factuality$Participant))

# Define the desired order of variables
variable_order <- rev(c( "Other.Errors", "Content.Verifiability.Errors", "Discourse.Errors", "Semantic.Frame.Errors")) #"No Errors",

# Reorder the columns based on the desired order
# factuality <- factuality[, c("Participant", variable_order)]


# Melt the data frame to long format
data_long <- reshape2::melt(factuality, id.vars = "Participant") %>%
  mutate("Error Type" = variable)

# Reorder the levels of the "Error Type" column
# data_long$`Error Type` <- factor(data_long$`Error Type`, levels = variable_order)


# Create the stacked bar charts
ggplot(data_long, aes(x = value, y = Participant, fill = `Error Type`)) +
  geom_bar(stat = "identity") +
  labs(title = "Factuality Errors by Participant Summary",
       x = "Percentage of Factuality Errors Present in Baseline Summary",
       y = NULL) +
  scale_fill_manual(values = c("#570047", "#a8194b", "#e55838", "#ffa600"), #c("#FF0000", "#00FF00", "#0000FF", "#FFFF00")) + #, "#FFFFFF")) +
                    # breaks = variable_order,
                    # labels = variable_order)+
  )+
  xlim(0, 100)+
  theme_minimal()+
  theme(legend.position = c(0.75, 0.5))
ggsave(paste0(folder,"factuality.png"), width = 6, height = 3 )
 
