

class SpeedPipelineMixin:
    ...
    # def 
    # img_counter = 1
    # for image in data_to_save.images:
    #     file_name = ProductImage.create_file_name(product.product_name, img_counter)                
    #     image_tuple = await ProductImage.get_or_create(product=product, file_name=file_name)
    #     image_instance = image_tuple[0]
    #     if image_tuple[1]:
    #         image_instance.save_image_file(
    #             binary_data=image.image, 
    #             supplier_enum=self.get_supplier_enum(data_to_save)
    #         )
    #     img_counter += 1
