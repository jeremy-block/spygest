library(dplyr)
library(tidytext)
library(forcats)
library(ggplot2)
library(tidyr)

folder = "figs/v4/"
personFilter = 1
for (personFilter in c(1,2,3)){
  
corpus_by_audience <- read.csv("data/data.csv") %>%
  filter(ground_truth == "manual" & person == personFilter) %>% #just look at the 16 summaries for specified participant
  select(final_summary,audience,person) %>%
  mutate(corpora = as.character(final_summary)) %>%
  select(-final_summary) %>%
  unnest_tokens(words, corpora) %>%
  count(audience, words, sort = TRUE)

corpus_by_example <- read.csv("data/data.csv") %>%
  filter(ground_truth == "manual" & person == personFilter) %>% #just look at the 16 summaries for specified participant
  select(final_summary,example) %>%
  mutate(corpora = as.character(final_summary)) %>%
  select(-final_summary) %>%
  unnest_tokens(words, corpora) %>%
  count(example, words, sort = TRUE)

total_words_by_audience <- corpus_by_audience %>% 
  group_by(audience) %>% 
  summarize(total = sum(n))

total_words_by_example <- corpus_by_example %>% 
  group_by(example) %>% 
  summarize(total = sum(n))

audience_words <- left_join(corpus_by_audience, total_words_by_audience)
example_words <- left_join(corpus_by_example, total_words_by_example)

audience_tf_idf <- audience_words %>%
  bind_tf_idf(words, audience, n)


example_tf_idf <- example_words %>%
  bind_tf_idf(words, example, n)




audience_tf_idf %>%
  group_by(audience) %>%
  slice_max(tf_idf, n = 10) %>%
  ungroup() %>%
  ggplot(aes(tf_idf, fct_reorder(words, tf_idf), fill = audience)) +
  geom_col(show.legend = FALSE) +
  facet_wrap(~audience, ncol = 2, scales = "free") +
  labs(title = paste0("TFIDF by Audience for Person ",personFilter), x = "tf-idf", y = NULL)
ggsave(paste0(folder,"TFIDF-Audence-",personFilter,".png"))

example_tf_idf %>%
  group_by(example) %>%
  slice_max(tf_idf, n = 10) %>%
  ungroup() %>%
  ggplot(aes(tf_idf, fct_reorder(words, tf_idf), fill = example)) +
  geom_col(show.legend = FALSE) +
  facet_wrap(~example, ncol = 2, scales = "free") +
  labs(title = paste0("TFIDF by Example for Person ",personFilter), x = "tf-idf", y = NULL)
ggsave(paste0(folder,"TFIDF-Example-",personFilter,".png"))

#####
# Bigrams

the_bigrams <- read.csv("data/data.csv") %>%
  filter(ground_truth == "manual" & person == personFilter) %>%  #just look at the 16 summaries for specified participant
  select(final_summary,audience) %>%
  mutate(corpora = as.character(final_summary)) %>%
  select(-final_summary) %>%
  unnest_tokens(bigram, corpora, token = "ngrams", n = 2) %>%
  filter(!is.na(bigram))

bigrams_filtered <- the_bigrams %>%
  separate(bigram, c("word1", "word2"), sep = " ") #%>%
  # filter(!word1 %in% stop_words$word) %>%
  # filter(!word2 %in% stop_words$word)

bigram_counts <- bigrams_filtered %>% 
  count(word1, word2, sort = TRUE)

bigrams_united <- bigrams_filtered %>%
  unite(bigram, word1, word2, sep = " ")

bigram_tf_idf <- bigrams_united %>%
  count(audience, bigram) %>%
  bind_tf_idf(bigram, audience, n) %>%
  arrange(desc(tf_idf))

bigram_tf_idf %>%
  group_by(audience) %>%
  slice_max(tf_idf, n = 9) %>%
  ungroup() %>%
  ggplot(aes(n, fct_reorder(bigram, n), fill = audience)) +
  geom_col(show.legend = FALSE) +
  facet_wrap(~audience, ncol = 2, scales = "free_y") +
  labs(title = paste0("Bigram TFIDF by Audience for Person ",personFilter), x = "tf-idf of Bigrams displayed with counts", caption = "showing the most popular bigrams for 4 summaries by audience. no stop words are filtered", y = NULL)
ggsave(paste0(folder,"Bigram-TFIDF-Audence-",personFilter,".png"))




the_bigrams <- read.csv("data/data.csv") %>%
  filter(ground_truth == "manual" & person == personFilter) %>%  #just look at the 16 summaries for specified participant
  select(final_summary,example) %>%
  mutate(corpora = as.character(final_summary)) %>%
  select(-final_summary) %>%
  unnest_tokens(bigram, corpora, token = "ngrams", n = 2) %>%
  filter(!is.na(bigram))

bigrams_filtered <- the_bigrams %>%
  separate(bigram, c("word1", "word2"), sep = " ") %>%
  filter(!word1 %in% stop_words$word) %>%
  filter(!word2 %in% stop_words$word)

bigram_counts <- bigrams_filtered %>% 
  count(word1, word2, sort = TRUE)

bigrams_united <- bigrams_filtered %>%
  unite(bigram, word1, word2, sep = " ")

bigram_tf_idf <- bigrams_united %>%
  count(example, bigram) %>%
  bind_tf_idf(bigram, example, n) %>%
  arrange(desc(tf_idf))

bigram_tf_idf %>%
  group_by(example) %>%
  slice_max(tf_idf, n = 9) %>%
  ungroup() %>%
  ggplot(aes(n, fct_reorder(bigram, n), fill = example)) +
  geom_col(show.legend = FALSE) +
  facet_wrap(~example, ncol = 2, scales = "free_y") +
  labs(title = paste0("Bigram TFIDF by Audience for Person ",personFilter), x = "tf-idf of Bigrams displayed with counts", caption = "showing the most popular bigrams for 4 summaries by audience. no stop words are filtered", y = NULL)
ggsave(paste0(folder,"Bigram-TFIDF-Audence-",personFilter,".png"))

}

