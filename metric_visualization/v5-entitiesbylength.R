# Load required packages
library(ggplot2)
library(dplyr)

# Read the CSV file
data <- read.csv("data/entityCounts.csv")

folder = "figs/v5/"
personFilter = 1
for (personFilter in c(1,2,3)){
  
data %>%
  filter(person == personFilter) %>% # & entity_type == "TOTAL") %>%
  # summary()
  ggplot( aes(x = audience, y = over_summary_length, fill = audience)) +
  geom_boxplot() +
  facet_wrap(~entity_type, nrow= 4, scales = "free")+
  labs(title = paste0("Entities by Audience for Paricipant",personFilter), x = "Audience", y = "Counts Over Summary Length")
  ggsave(paste0(folder,"Entities-Audience-",personFilter,".png"))
  
  data %>%
    filter(person == personFilter) %>% # & entity_type == "TOTAL") %>%
    ggplot( aes(x = example, y = over_summary_length, fill = example)) +
    geom_boxplot() +
    facet_wrap(~entity_type, nrow= 4, scales = "free")+
    labs(title = paste0("Entities by Example for Paricipant",personFilter), x = "Example", y = "Counts Over Summary Length")
  ggsave(paste0(folder,"Entities-Example-",personFilter,".png"))
  
  # scale_fill_manual(values = c("gray80", "gray40")) +
  # theme_minimal()
}



