<?php
set_time_limit(0);
while(true) {
    system('scrapy crawl pic');
    sleep(0.8);
}
