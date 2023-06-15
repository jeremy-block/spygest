# install.packages("DataExplorer")
library(DataExplorer)

# install.packages("GGally")
library(GGally)

# Load other required packages
library(ggplot2)
library(dplyr)

# Read the CSV file
data <- read.csv("data/data-manually-modified.csv")

# Set Data columns as factors and levels
data$audience <- factor(data$audience)
data$example <- factor(data$example)
data$person <- factor(data$person)
data$ground_truth <- factor(data$ground_truth)

levels(data$audience) <- c("None", "Self", "Peer", "Manager")
levels(data$example) <- c("None", "Manual", "Manual Masked", "Template Masked")
levels(data$person) <- c("P1","P2") #,"P3")
levels(data$ground_truth) <- c("manual", "baseline", "additional")



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
  ggpairs(mapping = aes(color = data$audience, alpha = 0.5))+
  labs(title=paste0("Correlations by ","Audience"))

print(p)
ggsave(filename = paste0(folder,"Pairwise by ", "Audience",".png"), plot = p)


p <- data %>%
  select(5:length(.)) %>%
  ggpairs(mapping = aes(color = data$example, alpha = 0.5))+
  labs(title=paste0("Correlations by ","Example Type"))

print(p)
ggsave(filename = paste0(folder,"Pairwise by ", "Example Type",".png"), plot = p)

p <- data %>%
  select(5:length(.)) %>%
  ggpairs(mapping = aes(color = data$person, alpha = 0.5))+
  labs(title=paste0("Correlations by ","Participant Number"))

print(p)
ggsave(filename = paste0(folder,"Pairwise by ", "Participant Number",".png"), plot = p)

p <- data %>%
  select(5:length(.)) %>%
  ggpairs(mapping = aes(color = data$ground_truth, alpha = 0.5))+
  labs(title=paste0("Correlations by ","Ground Truth"))

print(p)
ggsave(filename = paste0(folder,"Pairwise by ", "Ground Truth",".png"), plot = p)

