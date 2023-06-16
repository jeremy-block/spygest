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
  gather(key = "metric", value = "Score", character_count, word_count, rouge, bleu, bleurt, ter) %>%
  mutate(Audience = audience) %>%
  select(-audience) %>%
  mutate(Example = example) %>%
  select(-example)
    
gatheredMetrics$metric <- factor(gatheredMetrics$metric)
levels(gatheredMetrics$metric) <- c("Characters","Words","ROUGE", "BLEU", "BLEURT", "TER")
    
gatheredMetrics %>%
  ggplot(aes(x = Audience, y = Score, fill = Audience)) + 
  geom_boxplot() +
  facet_wrap(~metric, scales = "free") + 
  labs(title = "Accuracy Measures by Audience")
  
gatheredMetrics %>%
  ggplot(aes(x = Example, y = Score, fill = Example)) + 
  geom_boxplot() +
  facet_wrap(~metric, scales = "free") + 
  labs(title = "Accuracy Measures by Example")
