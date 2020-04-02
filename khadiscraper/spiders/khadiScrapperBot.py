# -*- coding: utf-8 -*-
import scrapy
import json


class KhadiscrapperbotSpider(scrapy.Spider):
    name = 'khadiScrapperBot'
    allowed_domains = ['www.pk.khaadi.com/']
    start_urls = ['https://pk.khaadi.com/ready-to-wear/pret.html']
    download_delay = 1

    def parse(self, response):
        products_list = self.get_products_list(response)

        # Now scrapping each product with their details
        for product in products_list:
            yield scrapy.Request(url=product, dont_filter=True, callback=self.find_product_images)

        # Scraping the other page
        page = self.get_pages(response)
        if page != None:
            yield scrapy.Request(url=page, dont_filter=True, callback=self.parse)      
            # return request



    def get_pages(self, response):
        page = response.css('li.item.pages-item-next a.action.next::attr(href)').extract_first()

        return page

    def get_products_list(self, response):
        products = response.css('a.product.photo.product-item-photo::attr(href)').extract()
            
        return products

    def find_product_images(self, response):

        product_details = {}
        img_url = response.xpath('//div[@class="product item-image imgzoom"]/img/@src').extract_first()
        product_details["image"] = img_url
        sku = response.css('div.product-sub-infomation.custom-sku-wrapper div.product.attribute.sku span.value::text').extract()
        product_details["sku"] = sku
        name = response.css('h1.product-name::text').extract()
        product_details["name"] = name
        price = response.css('span.price-container.price-final_price.tax.weee span.price-wrapper span.price::text').extract_first()
        product_details["price"] = price
        description  = response.css('div.product.attribute.overview div.value.std::text').extract()
        product_details["description"] = description

        # For colors

        data = response.xpath('//div[@class="product-add-form"]/form/div/div/script/text()').extract()
        json_text = json.loads(data[0])
        # If it gives error like unable to extract color the comment the color_dic line and print below variable, now find the approptiate key like i used 93 and it will work again same for sizes
        # color_dic = json_text["[data-role=swatch-options]"]["Magento_Swatches/js/swatch-renderer"]["jsonConfig"]["attributes"]
        # print(color_dic)

        color_dic = json_text["[data-role=swatch-options]"]["Magento_Swatches/js/swatch-renderer"]["jsonConfig"]["attributes"]["93"]["options"]
        product_colors = []
        if color_dic != None:
            for data in color_dic:
                if len(data["products"]) != 0:
                    product_colors.append(data["label"])

        product_details["colors"] = product_colors
        
        # for sizes
        data = response.xpath('//div[@class="product-add-form"]/form/div/div/script/text()').extract()
        json_text = json.loads(data[0])
        size_dic = json_text["[data-role=swatch-options]"]["Magento_Swatches/js/swatch-renderer"]["jsonConfig"]["attributes"]["153"]["options"]
        product_sizes = []
        if size_dic != None:
            for data in size_dic:
                if len(data["products"]) != 0:
                    product_sizes.append(data["label"])

        product_details["available sizes"] = product_sizes

        print(product_details)
        yield product_details
