from manim import *


class EnhancedHowItWorks(Scene):
    def construct(self):
        # Title
        title = Text("GitHub Trending Repository Analyzer", color=YELLOW)
        subdesc = Text("How does It Work?", color=YELLOW_B).scale(0.7)
        subdesc.next_to(title, DOWN, buff=0.5)
        title.to_edge(UP)
        self.play(Write(title))
        self.play(Write(subdesc))
        self.wait(1)

        # Step 1: Data Collection
        step1 = Text("1. Data Collection", color=BLUE).next_to(title, DOWN, buff=0.5)
        github_icon = Text("GitHub API", color=GREEN).next_to(step1, DOWN, buff=0.5)
        arrow1 = Arrow(github_icon.get_bottom(), ORIGIN + DOWN)
        data = Text("Raw Data", color=RED).next_to(arrow1, DOWN)

        self.play(FadeOut(subdesc))
        self.play(FadeIn(github_icon), GrowArrow(arrow1), FadeIn(data))
        self.wait(1)

        # Step 2: Data Processing
        step2 = Text("2. Data Processing", color=BLUE).next_to(data, DOWN, buff=0.5)
        process_icon = Text("Clean & Organize", color=GREEN).next_to(
            step2, DOWN, buff=0.5
        )
        arrow2 = Arrow(process_icon.get_bottom(), ORIGIN + DOWN * 5)
        processed_data = Text("Structured Data", color=RED).next_to(arrow2, DOWN)

        self.play(Write(step2))
        self.play(FadeIn(process_icon), GrowArrow(arrow2), FadeIn(processed_data))
        self.wait(1)

        # Step 3: Visualization

        step3 = Text("3. Data Visualization", color=BLUE).to_edge(LEFT).shift(UP)
        chart_icon = Text("Plotly Charts", color=GREEN).next_to(step3, DOWN, buff=0.5)
        chart = Square(side_length=1, color=YELLOW).next_to(chart_icon, DOWN, buff=0.5)

        self.play(Transform(step1, step3), FadeOut(data))
        self.play(Transform(github_icon, chart_icon), Transform(arrow1, chart))
        self.wait(1)

        # Step 4: AI Analysis
        step4 = Text("4. AI Analysis", color=BLUE).to_edge(RIGHT).shift(UP)
        ai_icon = Text("AI Model", color=GREEN).next_to(step4, DOWN, buff=0.5)
        insight = Text("Insights", color=RED).next_to(ai_icon, DOWN, buff=0.5)

        self.play(Transform(step2, step4))
        self.play(Transform(process_icon, ai_icon), Transform(processed_data, insight))
        self.wait(1)

        final_group = VGroup(
            step1,
            github_icon,
            arrow1,
            step2,
            process_icon,
            arrow2,
            processed_data,
            step3,
            chart_icon,
            chart,
            step4,
            ai_icon,
            insight,
        )
        self.play(FadeOut(final_group))

        # Step 5: Web Interface
        step5 = Text("5. Web Interface", color=BLUE).to_edge(DOWN)
        self.play(Write(step5))
        self.wait(1)

        # Create a more detailed browser window
        browser = RoundedRectangle(
            height=4.8, width=5.8, corner_radius=0.1, color=WHITE
        )
        browser.move_to(ORIGIN)

        # Add browser elements
        address_bar = Rectangle(height=0.3, width=5.6, color=GRAY)
        address_bar.move_to(browser.get_top() + DOWN * 0.2)

        # Create UI elements
        title = Text("GitHub Trending Analyzer", color=YELLOW, font_size=24)
        title.next_to(address_bar, DOWN, buff=0.2)

        table = Rectangle(height=1.5, width=5.3, color=WHITE)
        table.next_to(title, DOWN, buff=0.2)

        chart = RoundedRectangle(height=0.5, width=5.3, corner_radius=0.1, color=RED)
        chart.next_to(table, DOWN, buff=0.2)

        ai_insight = Rectangle(height=0.5, width=5.3, color=RED)
        ai_insight.next_to(chart, DOWN, buff=0.2)

        # Animate the creation of the UI
        self.play(Create(browser), Create(address_bar))
        self.play(Write(title))
        self.play(Create(table))
        self.play(Create(chart))
        self.play(Create(ai_insight))

        # Labels for UI elements
        table_label = Text("Interactive Data Table", font_size=16, color=WHITE).next_to(
            table, LEFT, buff=0.1
        )
        chart_label = Text("Visualizations", font_size=16, color=WHITE).next_to(
            chart, LEFT, buff=0.1
        )
        ai_label = Text("AI Insights", font_size=16, color=WHITE).next_to(
            ai_insight, LEFT, buff=0.1
        )

        self.play(Write(table_label), Write(chart_label), Write(ai_label))

        # Group all elements
        ui_group = VGroup(
            browser,
            address_bar,
            title,
            table,
            chart,
            ai_insight,
            table_label,
            chart_label,
            ai_label,
        )

        # Final animation
        self.play(ui_group.animate.scale(0.7).to_edge(RIGHT))
        self.wait(2)

        # Explanation text
        explanation = Text(
            "The web interface provides an intuitive dashboard\n"
            "with an interactive data table, dynamic visualizations,\n"
            "and AI-generated insights, allowing users to explore\n"
            "and analyze trending GitHub repositories effectively.",
            font_size=24,
            color=YELLOW,
        ).to_edge(LEFT)

        self.play(Write(explanation))
        self.wait(3)

        # Fade out
        self.play(FadeOut(ui_group), FadeOut(explanation), FadeOut(step5))
        self.wait(1)

        # Fade out
        self.play(FadeOut(title))
        self.wait(1)
