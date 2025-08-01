# flake8: noqa
from core.services.multi_reviews_service import MultiSourceReviewsService
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = (
        "Refresh reviews cache from TripAdvisor and Google APIs - "
        "runs daily via cron"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear-cache",
            action="store_true",
            help="Clear existing cache before fetching new reviews",
        )
        parser.add_argument(
            "--pages",
            type=int,
            default=3,
            help="Number of pages to preload (default: 3)",
        )
        parser.add_argument(
            "--per-page",
            type=int,
            default=7,
            help="Reviews per page (default: 7)",
        )

    def handle(self, *args, **options):
        """Main command handler - coordinates the refresh process"""
        start_time = timezone.now()
        self._print_start_message(start_time)

        try:
            service = MultiSourceReviewsService()
            self._handle_cache_clearing(service, options)

            total_reviews_loaded, sources_summary = self._load_reviews_pages(
                service, options
            )

            self._print_summary(
                service,
                start_time,
                total_reviews_loaded,
                sources_summary,
                options["pages"],
            )

            if total_reviews_loaded == 0:
                raise Exception("No reviews were loaded from any source")

        except Exception as e:
            self._handle_error(e)
            exit(1)

        self._print_completion_message()

    def _print_start_message(self, start_time):
        """Print the command start message"""
        self.stdout.write(
            self.style.SUCCESS(
                f"🚀 Starting reviews refresh at "
                f"{start_time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
        )

    def _handle_cache_clearing(self, service, options):
        """Clear cache if requested"""
        if options["clear_cache"]:
            service.clear_cache()
            self.stdout.write(self.style.WARNING("🗑️  Cache cleared"))

    def _load_reviews_pages(self, service, options):
        """Load reviews from multiple pages and return summary data"""
        pages_to_load = options["pages"]
        per_page = options["per_page"]
        total_reviews_loaded = 0
        sources_summary = {"tripadvisor": 0, "google": 0, "fallback": 0}

        for page in range(1, pages_to_load + 1):
            self.stdout.write(f"📄 Loading page {page}...")

            try:
                reviews_data = service.get_reviews(
                    page=page,
                    per_page=per_page,
                )

                if not self._process_page_reviews(reviews_data, page, sources_summary):
                    break

                total_reviews_loaded += len(reviews_data.get("reviews", []))

                if not reviews_data.get("has_next", False):
                    self._print_no_more_pages_message(page)
                    break

            except Exception as e:
                self._print_page_error(page, e)
                continue

        return total_reviews_loaded, sources_summary

    def _process_page_reviews(self, reviews_data, page, sources_summary):
        """Process reviews for a single page and update summary"""
        if not reviews_data or not reviews_data.get("reviews"):
            self.stdout.write(
                self.style.WARNING(f"   ⚠️  Page {page}: No reviews returned")
            )
            return False

        page_reviews = reviews_data["reviews"]
        reviews_count = len(page_reviews)

        # Update sources summary
        for review in page_reviews:
            source = review.get("source", "fallback")
            sources_summary[source] = sources_summary.get(source, 0) + 1

        # Print page success message
        sources_used = reviews_data.get("sources_used", {})
        sources_list = [k for k, v in sources_used.items() if v]
        sources_text = ", ".join(sources_list) if sources_list else "fallback"

        self.stdout.write(
            self.style.SUCCESS(
                f"   ✅ Page {page}: {reviews_count} reviews loaded "
                f"(Sources: {sources_text})"
            )
        )
        return True

    def _print_no_more_pages_message(self, page):
        """Print message when no more pages are available"""
        self.stdout.write(
            self.style.WARNING(f"   📄 No more pages available after page {page}")
        )

    def _print_page_error(self, page, error):
        """Print error message for a specific page"""
        self.stdout.write(self.style.ERROR(f"   ❌ Page {page}: Error - {str(error)}"))

    def _print_summary(
        self,
        service,
        start_time,
        total_reviews_loaded,
        sources_summary,
        pages_requested,
    ):
        """Print the complete summary of the refresh operation"""
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("📊 REFRESH SUMMARY"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(f"⏱️  Duration: {duration:.1f} seconds")
        self.stdout.write(f"📄 Pages loaded: {min(pages_requested, 99)}")
        self.stdout.write(f"📝 Total reviews: {total_reviews_loaded}")

        if total_reviews_loaded > 0:
            self._print_sources_breakdown(sources_summary, total_reviews_loaded)

        self._print_api_status(service)

        if total_reviews_loaded > 0:
            self.stdout.write("")
            self.stdout.write(
                self.style.SUCCESS(
                    f"🎉 SUCCESS: Reviews cache refreshed with "
                    f"{total_reviews_loaded} reviews!"
                )
            )

    def _print_sources_breakdown(self, sources_summary, total_reviews_loaded):
        """Print breakdown of reviews by source"""
        self.stdout.write("")
        self.stdout.write("📊 Sources breakdown:")
        for source, count in sources_summary.items():
            if count > 0:
                percentage = (count / total_reviews_loaded) * 100
                icon = self._get_source_icon(source)
                self.stdout.write(
                    f"   {icon} {source.title()}: {count} "
                    f"reviews ({percentage:.1f}%)"
                )

    def _get_source_icon(self, source):
        """Get appropriate icon for the source"""
        if source == "tripadvisor":
            return "🟢"
        elif source == "google":
            return "🔵"
        else:
            return "⚪"

    def _print_api_status(self, service):
        """Print the status of API configurations"""
        sources_status = service._get_sources_status()
        self.stdout.write("")
        self.stdout.write("🔧 API Status:")

        ta_status = (
            "✅ Configured"
            if sources_status.get("tripadvisor")
            else "❌ Missing API key"
        )
        self.stdout.write(f"   TripAdvisor: {ta_status}")

        google_status = (
            "✅ Configured" if sources_status.get("google") else "❌ Missing API key"
        )
        self.stdout.write(f"   Google Places: {google_status}")

    def _handle_error(self, error):
        """Handle and debug errors during the refresh process"""
        self.stdout.write("")
        self.stdout.write(self.style.ERROR(f"💥 FAILED: {str(error)}"))
        self.stdout.write("")
        self.stdout.write(self.style.WARNING("🔍 Debugging info:"))

        try:
            service = MultiSourceReviewsService()
            self._print_debug_info(service)
        except Exception as debug_e:
            self.stdout.write(f"   Debug failed: {str(debug_e)}")

    def _print_debug_info(self, service):
        """Print debugging information about API sources"""
        sources_status = service._get_sources_status()
        self.stdout.write(
            f"   TripAdvisor API configured: "
            f"{sources_status.get('tripadvisor', False)}"
        )
        self.stdout.write(
            f"   Google API configured: " f"{sources_status.get('google', False)}"
        )

        self.stdout.write("")
        self.stdout.write("🧪 Testing individual sources:")

        self._test_tripadvisor_source(service)
        self._test_google_source(service)

    def _test_tripadvisor_source(self, service):
        """Test TripAdvisor API source"""
        try:
            ta_reviews = service._fetch_tripadvisor_reviews()
            status = "✅" if ta_reviews else "❌"
            self.stdout.write(f"   TripAdvisor: {status} ({len(ta_reviews)} reviews)")
        except Exception as ta_e:
            self.stdout.write(f"   TripAdvisor: ❌ Error - {str(ta_e)}")

    def _test_google_source(self, service):
        """Test Google Places API source"""
        try:
            google_reviews = service._fetch_google_reviews()
            status = "✅" if google_reviews else "❌"
            self.stdout.write(f"   Google: {status} ({len(google_reviews)} reviews)")
        except Exception as g_e:
            self.stdout.write(f"   Google: ❌ Error - {str(g_e)}")

    def _print_completion_message(self):
        """Print command completion message"""
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("✨ Command completed successfully!"))
