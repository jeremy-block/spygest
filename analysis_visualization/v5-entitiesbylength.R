#####
# Examining the entities menitoned in the output summaries
# NOTE: Run v5-EntityExtractor.py before running this file.
# No significant results.
#####

# Load required packages
library(ggplot2)
library(dplyr)

# Read the CSV file
data <- read.csv("data/entityCounts.csv")

folder <- "figs/v5/"
person_filter <- 1
for (person_filter in c(1, 2, 3)){
  data %>%
    filter(person == person_filter) %>% # & entity_type == "TOTAL") %>%
    ggplot(aes(x = audience, y = over_summary_length, fill = audience)) +
    geom_boxplot() +
    facet_wrap(~entity_type, nrow = 4, scales = "free") +
    labs(title = paste0("Entities by Audience for Paricipant", person_filter), x = "Audience", y = "Counts Over Summary Length")
    ggsave(paste0(folder, "Entities-Audience-", person_filter, ".png"))

    data %>%
      filter(person == person_filter) %>% # & entity_type == "TOTAL") %>%
      ggplot(aes(x = example, y = over_summary_length, fill = example)) +
      geom_boxplot() +
      facet_wrap(~entity_type, nrow = 4, scales = "free") +
      labs(title = paste0("Entities by Example for Paricipant", person_filter), x = "Example", y = "Counts Over Summary Length")
    ggsave(paste0(folder, "Entities-Example-", person_filter, ".png"))
}
