library(tidyverse)
library(rvest)
library(RSelenium) # to get the loaded html of 

### scrape the address data

##### selenium

### open
rD <- rsDriver(browser=c("chrome"), chromever="71.0.3578.80", verbose = FALSE, port = as.integer(4559))
# binman::list_versions("chromedriver")

### login
remDr <- rD$client
url_login <- "https://m.facebook.com/login.php"
remDr$navigate(url_login)

#send username
username <- remDr$findElement(using = "id", value = "m_login_email")
username$sendKeysToElement(list("dennistsengchocho@gmail.com"))

#send password and Enter
passwd <- remDr$findElement(using = "id", value = "m_login_password")
passwd$sendKeysToElement(list("personlottery", "\uE007"))

url_ntu <- "https://m.facebook.com/ntusociology/"
remDr$navigate(url_ntu)

### scroll down
webElem <- remDr$findElement("css", "body")
for (i in 1:10) {
  webElem$sendKeysToElement(list(key = "end"))
  Sys.sleep(3)
}

### get post links
html_obj <- remDr$getPageSource(header = TRUE)[[1]] %>% read_html()
links = html_obj %>% html_nodes("._5msj") %>% html_attr('href')
links_f = str_c("https://m.facebook.com", links)

time <- list()
text <- list()
thumb <- list()
share <- list()
comment <- list()
meta <- list()

for (i in 1:length(links_f)) {
  
  remDr$navigate(links_f[i])
  html_obj_post <- remDr$getPageSource(header = TRUE)[[1]] %>% read_html()
  
  time[i] <- html_obj_post %>% html_nodes("._52jc") %>% html_text() %>% `[`(1)
  text[i] <- html_obj_post %>% html_nodes("._5rgt._5nk5") %>% html_text() %>% `[`(1)
  thumb[i] <- html_obj_post %>% html_nodes("._1g06") %>% html_text()
  share[i] <- html_obj_post %>% html_nodes("._43lx") %>% html_text()
  meta[i] <- html_obj_post %>% html_nodes("._52jh._5ton._45m7") %>% html_text()
  html_obj_post %>% html_nodes("._333v._45kb") %>% html_text()
  Sys.sleep(3)
}

df_fbpost <- tibble(time = unlist(time),
                    text = unlist(text),
                    thumb = unlist(thumb),
                    share = unlist(share),
                    meta = unlist(meta))

rD$server$stop()
rm(rD);gc()

df_fbpost %>% write_rds("")
df_fbpost %>% write_csv("")
