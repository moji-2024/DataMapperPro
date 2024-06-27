import sqlDB
import models
import manager

class product_category(models.model):
    title = models.CharField(max_length=300)
class_product_tag = type(f'product_tag', (models.model,),
                     {'title': models.CharField(max_length=300),})

class product(models.model):
    category = models.ForeignKey(product_category, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=300)
    price = models.DecimalField()
    tag = models.ManyToManyField(class_product_tag, null=True)
# create tables
manager.manager.create_tabels()

#insert rows to tables
for tag in ['tag1','tag2','tag3',]:
    create_tag = class_product_tag(title=tag)
    create_tag.save()
for category in ['category1','category2','category3',]:
    create_category = product_category(title=category)
    create_category.save()
for prod,price in [('product1',100.23),('product2',200.23),('product3',300.23),]:
    create_product = product(title=prod,price=price)
    create_product.save()

# return objects by rows from tables
all_product = product().objects.all()
all_categories= product_category().objects.all()
all_tags = class_product_tag().objects.all()

# make connection between tables
for index ,pro in enumerate(all_product):
    pro.category.update(all_categories[index])
    if index == 0:
        pro.tag.add(all_tags[0])
    elif index == 1:
        pro.tag.add(all_tags[0])
        pro.tag.add(all_tags[1])
    else:
        pro.tag.add(all_tags[0])
        pro.tag.add(all_tags[1])
        pro.tag.add(all_tags[2])

# return data to use
p = product().objects.filter(category__title='category2').order_by('price')
print(p[0].title)
t = p[0].tag.filter(title='tag1')
print(t)
print(t[0].title)
first_product_set_to_tag1 = t[0].product_set.all()[0]
print(first_product_set_to_tag1)
category_related_to_first_product_set_to_tag1 = first_product_set_to_tag1.category.get()
print(category_related_to_first_product_set_to_tag1)
