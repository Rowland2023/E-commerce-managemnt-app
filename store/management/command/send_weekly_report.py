from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from store.models import Order, Product

class Command(BaseCommand):
    def handle(self, *args, **options):
        last_week = timezone.now() - timedelta(days=7)
        
        # 1. Gather Data
        total_sales = Order.objects.filter(complete=True, date_order__gte=last_week).aggregate(Sum('total_due'))['total_due__sum'] or 0
        order_count = Order.objects.filter(date_order__gte=last_week).count()
        low_stock_count = Product.objects.filter(stock_quantity__lt=5).count()

        # 2. Render HTML
        context = {
            'total_sales': total_sales,
            'order_count': order_count,
            'low_stock_count': low_stock_count,
            'project_name': 'E-Commerce Store'
        }
        html_content = render_to_string('emails/weekly_report.html', context)
        text_content = strip_tags(html_content)  # Fallback for old email clients

        # 3. Create Email
        email = EmailMultiAlternatives(
            subject=f"Weekly Report - {timezone.now().strftime('%b %d, %Y')}",
            body=text_content,
            from_email='noreply@yourdomain.com',
            to=['admin@yourdomain.com']
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

        self.stdout.write(self.style.SUCCESS('HTML report sent successfully!'))