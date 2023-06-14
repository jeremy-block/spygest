# install.packages("DataExplorer")
library(DataExplorer)

# install.packages("GGally")
library(GGally)

# Load other required packages
library(ggplot2)
library(dplyr)

# Read the CSV file
data <- read.csv("data/randomValues.csv")

# Set Data columns as factors and levels
data$Audience <- factor(data$Audience)
data$Example.Type <- factor(data$Example.Type)
data$User.Number <- factor(data$User.Number)
data$Ground.Truth <- factor(data$Ground.Truth)

levels(data$Audience) <- c("None", "Self", "Peer", "Manager")
levels(data$Example.Type) <- c("None", "Manual", "Manual Masked", "Template Masked")
levels(data$User.Number) <- c("P1","P2","P3")
levels(data$Ground.Truth) <- c("manual", "baseline", "additional")



# Exploritory Data Analysis Reports by each categorical variable
categorical.vars <- colnames(data)[0:4]

for(i in categorical.vars){
  print(i)
data %>%
  create_report(
    output_file = paste0("EDA ",i, format(Sys.time(), "--%Y-%m-%d %H.%M.%S %Z")),
    report_title = paste0("Report - ",i),
    y = i
  )
}


# Each Qualitative Comparison as images.
folder <- "figs/v3/"
options(repr.plot.width = 20, repr.plot.height = 10)

p <- data %>%
  select(5:length(.)) %>%
  ggpairs(mapping = aes(color = data$Audience, alpha = 0.5))+
  labs(title=paste0("Comparisons by ","Audience"))

print(p)
ggsave(filename = paste0(folder,"Pairwise by ", "Audience",".png"), plot = p)


p <- data %>%
  select(5:length(.)) %>%
  ggpairs(mapping = aes(color = data$Example.Type, alpha = 0.5))+
  labs(title=paste0("Comparisons by ","Example Type"))

print(p)
ggsave(filename = paste0(folder,"Pairwise by ", "Example Type",".png"), plot = p)

p <- data %>%
  select(5:length(.)) %>%
  ggpairs(mapping = aes(color = data$User.Number, alpha = 0.5))+
  labs(title=paste0("Comparisons by ","Participant Number"))

print(p)
ggsave(filename = paste0(folder,"Pairwise by ", "Participant Number",".png"), plot = p)

p <- data %>%
  select(5:length(.)) %>%
  ggpairs(mapping = aes(color = data$Ground.Truth, alpha = 0.5))+
  labs(title=paste0("Comparisons by ","Ground Truth"))

print(p)
ggsave(filename = paste0(folder,"Pairwise by ", "Ground Truth",".png"), plot = p)

