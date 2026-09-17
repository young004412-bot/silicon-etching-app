import streamlit as st
import pandas as pd
import numpy as np

# =========================
# Page configuration
# =========================
st.set_page_config(
    page_title="Silicon Etching Rate Analyzer",
    page_icon="🔬",
    layout="centered"
)

# =========================
# Title
# =========================
st.title("🔬 Silicon Etching Rate Analyzer")

st.write(
    "A web-based tool for evaluating silicon etching rate "
    "under different experimental conditions."
)

st.divider()

# =========================================================
# PART 1 — Single Experiment Calculator
# =========================================================

st.header("1. Single Experiment Calculator")

thickness_unit = st.selectbox(
    "Thickness Unit",
    ["μm", "nm", "mm"]
)
initial_thickness = st.number_input(
    f"Initial Si Thickness ({thickness_unit})",
    min_value=0.0,
    value=500.0,
    step=1.0
)

final_thickness = st.number_input(
    f"Final Si Thickness ({thickness_unit})",
    min_value=0.0,
    value=450.0,
    step=1.0
)

etching_time = st.number_input(
    "Etching Time (min)",
    min_value=0.001,
    value=10.0,
    step=1.0
)

thickness_uncertainty = st.number_input(
    "Thickness Uncertainty (± μm)",
    min_value=0.0,
    value=2.0,
    step=0.1
)

time_uncertainty = st.number_input(
    "Time Uncertainty (± min)",
    min_value=0.0,
    value=0.1,
    step=0.01
)
etchant = st.selectbox(
    "Etchant",
    [
        "KOH",
        "TMAH",
        "HF",
        "HNO₃/HF",
        "Other"
    ]
)

temperature = st.number_input(
    "Temperature (°C)",
    min_value=-273.15,
    value=80.0,
    step=1.0
)

wafer_orientation = st.selectbox(
    "Wafer Orientation",
    [
        "(100)",
        "(110)",
        "(111)"
    ]
)

if st.button("Calculate Etching Rate"):

    # Convert thickness to micrometers
    conversion_factor = {
        "μm": 1.0,
        "nm": 0.001,
        "mm": 1000.0
}

    initial_um = (
    initial_thickness
    * conversion_factor[thickness_unit]
)

    final_um = (
    final_thickness
    * conversion_factor[thickness_unit]
)

    thickness_removed = initial_um - final_um

    if thickness_removed < 0:

        st.error(
            "Error: Final thickness cannot be greater than "
            "initial thickness."
        )

    elif etching_time <= 0:

        st.error(
            "Error: Etching time must be greater than zero."
        )

    else:

        etching_rate = thickness_removed / etching_time

        # Uncertainty propagation
        thickness_error = thickness_uncertainty

        rate_uncertainty = (
        (
            (thickness_error / etching_time) ** 2
            +
            (
                thickness_removed
                * time_uncertainty
                / (etching_time ** 2)
            ) ** 2
        ) ** 0.5
    )
        etching_rate_nm_min = etching_rate * 1000
        etching_rate_um_hour = etching_rate * 60

        st.divider()

        st.subheader("Result")

        st.metric(
            "Silicon Etching Rate",
            f"{etching_rate:.2f} ± {rate_uncertainty:.2f} μm/min"
        )

        st.caption(
            "Uncertainty calculated using propagation of uncertainty."
        )
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Thickness Removed**")
            st.write(f"{thickness_removed:.2f} μm")

        with col2:
            st.write("**Etching Rate**")
            st.write(f"{etching_rate_nm_min:.2f} nm/min")

        st.write(
            f"Equivalent rate: "
            f"**{etching_rate_um_hour:.2f} μm/hour**"
        )

        st.divider()

        st.subheader("Experimental Conditions")

        st.write(f"**Etchant:** {etchant}")
        st.write(f"**Temperature:** {temperature:.1f} °C")
        st.write(f"**Wafer Orientation:** {wafer_orientation}")
        st.write(f"**Etching Time:** {etching_time:.2f} min")

        st.divider()

        st.subheader("Calculation")

        st.latex(
            r"""
            R = \frac{d_i-d_f}{t}
            """
        )

        st.write(
            f"R = ({initial_thickness:.2f} - "
            f"{final_thickness:.2f}) / "
            f"{etching_time:.2f}"
        )

        st.write(
            f"**R = {etching_rate:.2f} μm/min**"
        )


# =========================================================
# PART 2 — Experimental Data Analysis
# =========================================================

st.divider()

st.header("2. Experimental Data Analysis")

st.write(
    "Upload experimental data in CSV format, "
    "or enter data manually."
)

# =========================================================
# CSV Upload
# =========================================================

st.subheader("Upload Experimental Data")

uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=["csv"]
)

# =========================================================
# If CSV is uploaded
# =========================================================

if uploaded_file is not None:

    try:

        uploaded_data = pd.read_csv(uploaded_file)

        st.success(
            "CSV file uploaded successfully."
        )

        st.write("### Uploaded Data")

        st.dataframe(
            uploaded_data,
            width="stretch"
        )

        # Required columns
        required_columns = [
            "Temperature (°C)",
            "Initial Thickness (μm)",
            "Final Thickness (μm)",
            "Etching Time (min)"
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in uploaded_data.columns
        ]

        if missing_columns:

            st.error(
                "Missing required columns: "
                + ", ".join(missing_columns)
            )

        else:

            analysis_data = uploaded_data.copy()

            # Calculate removed thickness
            analysis_data["Thickness Removed (μm)"] = (
                analysis_data["Initial Thickness (μm)"]
                - analysis_data["Final Thickness (μm)"]
            )

            # Calculate etching rate
            analysis_data["Etching Rate (μm/min)"] = (
                analysis_data["Thickness Removed (μm)"]
                / analysis_data["Etching Time (min)"]
            )

            # Check invalid thickness
            if (
                analysis_data["Thickness Removed (μm)"] < 0
            ).any():

                st.error(
                    "Error: Final thickness cannot be greater "
                    "than initial thickness."
                )

            # Check invalid time
            elif (
                analysis_data["Etching Time (min)"] <= 0
            ).any():

                st.error(
                    "Error: Etching time must be greater than zero."
                )

            else:

                st.success(
                    "Experimental data analyzed successfully."
                )

                st.subheader(
                    "CSV Analysis Results"
                )

                st.dataframe(
                    analysis_data,
                    width="stretch"
                )

                # =========================
                # Statistics
                # =========================

                st.subheader(
                    "Statistical Summary"
                )

                average_rate = (
                    analysis_data[
                        "Etching Rate (μm/min)"
                    ].mean()
                )

                maximum_rate = (
                    analysis_data[
                        "Etching Rate (μm/min)"
                    ].max()
                )

                minimum_rate = (
                    analysis_data[
                        "Etching Rate (μm/min)"
                    ].min()
                )

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Average Rate",
                        f"{average_rate:.2f} μm/min"
                    )

                with col2:
                    st.metric(
                        "Maximum Rate",
                        f"{maximum_rate:.2f} μm/min"
                    )

                with col3:
                    st.metric(
                        "Minimum Rate",
                        f"{minimum_rate:.2f} μm/min"
                    )

                # =========================
                # Temperature plot
                # =========================

                st.subheader(
                    "Etching Rate vs. Temperature"
                )

                chart_data = analysis_data[
                    [
                        "Temperature (°C)",
                        "Etching Rate (μm/min)"
                    ]
                ].copy()

                chart_data = chart_data.sort_values(
                    "Temperature (°C)"
                )

                chart_data = chart_data.set_index(
                    "Temperature (°C)"
                )

                st.line_chart(
                    chart_data
                )
                # =========================
                # Arrhenius Analysis
                # =========================

                st.divider()

                st.subheader("Arrhenius Analysis")

                st.write(
                    "Arrhenius analysis is used to estimate "
                    "the activation energy of the silicon "
                    "etching process."
                )

                # Convert temperature from Celsius to Kelvin
                analysis_data["Temperature (K)"] = (
                    analysis_data["Temperature (°C)"] + 273.15
                )

                # Calculate 1/T
                analysis_data["1/T (K⁻¹)"] = (
                    1 / analysis_data["Temperature (K)"]
                )

                # Calculate ln(etching rate)
                analysis_data["ln(Etching Rate)"] = np.log(
                    analysis_data["Etching Rate (μm/min)"]
                )

                # Arrhenius analysis requires positive rates
                if (
                    analysis_data["Etching Rate (μm/min)"] <= 0
                ).any():

                    st.warning(
                        "Arrhenius analysis requires "
                        "positive etching rates."
                    )

                else:

                    # X = 1/T
                    x = analysis_data[
                        "1/T (K⁻¹)"
                    ].to_numpy()

                    # Y = ln(rate)
                    y = analysis_data[
                        "ln(Etching Rate)"
                    ].to_numpy()

                    # Linear regression
                    slope, intercept = np.polyfit(
                        x,
                        y,
                        1
                    )

                    # Predicted values
                    y_pred = slope * x + intercept

                    # R-squared
                    ss_res = np.sum(
                        (y - y_pred) ** 2
                    )

                    ss_tot = np.sum(
                        (y - np.mean(y)) ** 2
                    )

                    if ss_tot != 0:
                        r_squared = 1 - ss_res / ss_tot
                    else:
                        r_squared = 0.0

                    # Gas constant
                    gas_constant = 8.314

                    # Activation energy
                    activation_energy = (
                        -slope * gas_constant
                    )

                    # Convert J/mol to kJ/mol
                    activation_energy_kj = (
                        activation_energy / 1000
                    )

                    # =========================
                    # Results
                    # =========================

                    st.write("### Arrhenius Results")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric(
                            "Activation Energy",
                            f"{activation_energy_kj:.2f} kJ/mol"
                        )

                    with col2:
                        st.metric(
                            "R²",
                            f"{r_squared:.4f}"
                        )

                    st.write(
                        f"Regression slope: "
                        f"**{slope:.4e} K**"
                    )

                    st.write(
                        f"Regression intercept: "
                        f"**{intercept:.4f}**"
                    )

                    # =========================
                    # Arrhenius equation
                    # =========================

                    st.write("### Arrhenius Equation")

                    st.latex(
                        r"""
                        \ln(R)
                        =
                        \ln(A)
                        -
                        \frac{E_a}{R_g}
                        \frac{1}{T}
                        """
                    )

                    st.write(
                        f"Estimated activation energy: "
                        f"**{activation_energy_kj:.2f} kJ/mol**"
                    )

                    # =========================
                    # Arrhenius plot
                    # =========================

                    st.write("### Arrhenius Plot")

                    arrhenius_plot = pd.DataFrame(
                        {
                            "ln(Etching Rate)": y
                        },
                        index=x
                    )

                    arrhenius_plot.index.name = "1/T (K⁻¹)"

                    st.line_chart(
                        arrhenius_plot
                    )

                    # =========================
                    # Analysis table
                    # =========================

                    st.write(
                        "### Arrhenius Analysis Data"
                    )

                    st.dataframe(
                        analysis_data[
                            [
                                "Temperature (°C)",
                                "Temperature (K)",
                                "1/T (K⁻¹)",
                                "Etching Rate (μm/min)",
                                "ln(Etching Rate)"
                            ]
                        ],
                        width="stretch"
                    )

    except Exception as e:

        st.error(
            f"Unable to read the CSV file: {e}"
        )

# =========================================================
# PART 3 — Condition Comparison
# =========================================================

st.divider()

st.header("3. Condition Comparison")

st.write(
    "Compare silicon etching rates under different "
    "etchants and wafer orientations."
)

if uploaded_file is not None and "uploaded_data" in locals():

    comparison_data = uploaded_data.copy()

    required_comparison_columns = [
        "Temperature (°C)",
        "Initial Thickness (μm)",
        "Final Thickness (μm)",
        "Etching Time (min)"
    ]

    if all(
        column in comparison_data.columns
        for column in required_comparison_columns
    ):

        # Calculate etching rate
        comparison_data["Thickness Removed (μm)"] = (
            comparison_data["Initial Thickness (μm)"]
            - comparison_data["Final Thickness (μm)"]
        )

        comparison_data["Etching Rate (μm/min)"] = (
            comparison_data["Thickness Removed (μm)"]
            / comparison_data["Etching Time (min)"]
        )

        # =========================
        # Etchant filter
        # =========================

        if "Etchant" in comparison_data.columns:

            etchants = (
                comparison_data["Etchant"]
                .dropna()
                .unique()
                .tolist()
            )

            selected_etchant = st.selectbox(
                "Select Etchant",
                etchants
            )

        else:

            selected_etchant = None

        # =========================
        # Wafer orientation filter
        # =========================

        if "Wafer Orientation" in comparison_data.columns:

            orientations = (
                comparison_data["Wafer Orientation"]
                .dropna()
                .unique()
                .tolist()
            )

            selected_orientation = st.selectbox(
                "Select Wafer Orientation",
                orientations
            )

        else:

            selected_orientation = None

        # =========================
        # Filter data
        # =========================

        filtered_data = comparison_data.copy()

        if selected_etchant is not None:

            filtered_data = filtered_data[
                filtered_data["Etchant"]
                == selected_etchant
            ]

        if selected_orientation is not None:

            filtered_data = filtered_data[
                filtered_data["Wafer Orientation"]
                == selected_orientation
            ]

        # =========================
        # Display filtered data
        # =========================

        st.subheader(
            "Filtered Experimental Data"
        )

        st.dataframe(
            filtered_data,
            width="stretch"
        )

        # =========================
        # Statistics
        # =========================

        if len(filtered_data) > 0:

            average_rate = (
                filtered_data[
                    "Etching Rate (μm/min)"
                ].mean()
            )

            maximum_rate = (
                filtered_data[
                    "Etching Rate (μm/min)"
                ].max()
            )

            minimum_rate = (
                filtered_data[
                    "Etching Rate (μm/min)"
                ].min()
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Average Rate",
                    f"{average_rate:.2f} μm/min"
                )

            with col2:

                st.metric(
                    "Maximum Rate",
                    f"{maximum_rate:.2f} μm/min"
                )

            with col3:

                st.metric(
                    "Minimum Rate",
                    f"{minimum_rate:.2f} μm/min"
                )

            # =========================
            # Comparison chart
            # =========================

            st.subheader(
                "Etching Rate vs. Temperature"
            )

            comparison_chart = filtered_data[
                [
                    "Temperature (°C)",
                    "Etching Rate (μm/min)"
                ]
            ].copy()

            comparison_chart = (
                comparison_chart
                .sort_values("Temperature (°C)")
            )

            comparison_chart = (
                comparison_chart
                .set_index("Temperature (°C)")
            )

            st.line_chart(
                comparison_chart
            )
            # =========================
            # Multi-Etchant Comparison
            # =========================

            st.subheader(
                "Etchant Comparison"
            )

            comparison_all = comparison_data.copy()

            comparison_all["Etching Rate (μm/min)"] = (
                comparison_all[
                    "Thickness Removed (μm)"
                ]
                / comparison_all[
                    "Etching Time (min)"
                ]
            )

            multi_chart = comparison_all[
                [
                    "Temperature (°C)",
                    "Etchant",
                    "Etching Rate (μm/min)"
                ]
            ].copy()

            multi_chart = multi_chart.pivot_table(
                index="Temperature (°C)",
                columns="Etchant",
                values="Etching Rate (μm/min)",
                aggfunc="mean"
            )

            multi_chart = multi_chart.sort_index()

            st.line_chart(
                multi_chart
            )
            # =========================
            # Wafer Orientation Comparison
            # =========================

            st.subheader(
                "Wafer Orientation Comparison"
            )

            orientation_chart = comparison_data.copy()

            orientation_chart[
                "Etching Rate (μm/min)"
            ] = (
                orientation_chart[
                    "Thickness Removed (μm)"
                ]
                / orientation_chart[
                    "Etching Time (min)"
                ]
            )

            orientation_chart = orientation_chart[
                [
                    "Temperature (°C)",
                    "Wafer Orientation",
                    "Etching Rate (μm/min)"
                ]
            ].copy()

            orientation_chart = orientation_chart.pivot_table(
                index="Temperature (°C)",
                columns="Wafer Orientation",
                values="Etching Rate (μm/min)",
                aggfunc="mean"
            )

            orientation_chart = (
                orientation_chart.sort_index()
            )

            st.line_chart(
                orientation_chart
            )
# =========================
            # Experimental Summary
            # =========================

            st.subheader(
                "Experimental Summary"
            )

            summary_data = comparison_data.copy()

            summary_data["Etching Rate (μm/min)"] = (
                summary_data[
                    "Thickness Removed (μm)"
                ]
                / summary_data[
                    "Etching Time (min)"
                ]
            )

            summary_rate = summary_data[
                "Etching Rate (μm/min)"
            ]

            average_summary_rate = summary_rate.mean()
            maximum_summary_rate = summary_rate.max()
            minimum_summary_rate = summary_rate.min()

            hottest_temperature = summary_data[
                "Temperature (°C)"
            ].max()

            lowest_temperature = summary_data[
                "Temperature (°C)"
            ].min()

            hottest_rate = summary_data.loc[
                summary_data[
                    "Temperature (°C)"
                ].idxmax(),
                "Etching Rate (μm/min)"
            ]

            lowest_rate = summary_data.loc[
                summary_data[
                    "Temperature (°C)"
                ].idxmin(),
                "Etching Rate (μm/min)"
            ]

            st.write(
                f"The average silicon etching rate was "
                f"**{average_summary_rate:.2f} μm/min**."
            )

            st.write(
                f"The measured etching rate ranged from "
                f"**{minimum_summary_rate:.2f}** to "
                f"**{maximum_summary_rate:.2f} μm/min**."
            )

            st.write(
                f"At {lowest_temperature:.0f} °C, the calculated "
                f"etching rate was "
                f"**{lowest_rate:.2f} μm/min**, while at "
                f"{hottest_temperature:.0f} °C it was "
                f"**{hottest_rate:.2f} μm/min**."
            )

            st.info(
                "The summary is generated directly from "
                "the uploaded experimental data."
            )
            # =========================
            # PDF Report
            # =========================

            import io
            import matplotlib.pyplot as plt

            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import cm
            from reportlab.lib.utils import ImageReader

            # Create PDF buffer
            pdf_buffer = io.BytesIO()

            pdf = canvas.Canvas(
                pdf_buffer,
                pagesize=A4
            )

            width, height = A4

            # =========================
            # PAGE 1 - Report Summary
            # =========================

            pdf.setFont(
                "Helvetica-Bold",
                20
            )

            pdf.drawString(
                2 * cm,
                height - 2 * cm,
                "Silicon Etching Rate Analysis Report"
            )

            pdf.setFont(
                "Helvetica",
                11
            )

            pdf.drawString(
                2 * cm,
                height - 3.5 * cm,
                "Experimental Data Analysis"
            )

            pdf.drawString(
                2 * cm,
                height - 5 * cm,
                f"Average Etching Rate: "
                f"{average_summary_rate:.2f} um/min"
            )

            pdf.drawString(
                2 * cm,
                height - 6 * cm,
                f"Minimum Etching Rate: "
                f"{minimum_summary_rate:.2f} um/min"
            )

            pdf.drawString(
                2 * cm,
                height - 7 * cm,
                f"Maximum Etching Rate: "
                f"{maximum_summary_rate:.2f} um/min"
            )

            pdf.drawString(
                2 * cm,
                height - 8 * cm,
                f"Temperature Range: "
                f"{lowest_temperature:.0f} - "
                f"{hottest_temperature:.0f} C"
            )

            pdf.drawString(
                2 * cm,
                height - 9.5 * cm,
                "Experimental Summary"
            )

            pdf.setFont(
                "Helvetica",
                10
            )

            pdf.drawString(
                2 * cm,
                height - 11 * cm,
                f"The measured etching rate ranged from "
                f"{minimum_summary_rate:.2f} to "
                f"{maximum_summary_rate:.2f} um/min."
            )

            pdf.drawString(
                2 * cm,
                height - 12 * cm,
                f"At {lowest_temperature:.0f} C, the etching rate was "
                f"{lowest_rate:.2f} um/min."
            )

            pdf.drawString(
                2 * cm,
                height - 13 * cm,
                f"At {hottest_temperature:.0f} C, the etching rate was "
                f"{hottest_rate:.2f} um/min."
            )

            # =========================
            # PAGE 2 - Temperature Plot
            # =========================

            plot_buffer = io.BytesIO()

            plot_data = comparison_data.copy()

            plot_data["Etching Rate (um/min)"] = (
                plot_data["Thickness Removed (μm)"]
                / plot_data["Etching Time (min)"]
            )

            plot_data = plot_data.sort_values(
                "Temperature (°C)"
            )

            fig1, ax1 = plt.subplots()

            ax1.plot(
                plot_data["Temperature (°C)"],
                plot_data["Etching Rate (um/min)"],
                marker="o"
            )

            ax1.set_xlabel(
                "Temperature (°C)"
            )

            ax1.set_ylabel(
                "Etching Rate (um/min)"
            )

            ax1.set_title(
                "Silicon Etching Rate vs. Temperature"
            )

            fig1.tight_layout()

            fig1.savefig(
                plot_buffer,
                format="png",
                dpi=200
            )

            plt.close(fig1)

            plot_buffer.seek(0)

            pdf.showPage()

            pdf.setFont(
                "Helvetica-Bold",
                18
            )

            pdf.drawString(
                2 * cm,
                height - 2 * cm,
                "Etching Rate vs. Temperature"
            )

            pdf.drawImage(
                ImageReader(plot_buffer),
                2 * cm,
                height - 15 * cm,
                width=17 * cm,
                height=10 * cm,
                preserveAspectRatio=True,
                anchor="c"
            )

            # =========================
            # PAGE 3 - Etchant Comparison
            # =========================

            etchant_plot_buffer = io.BytesIO()

            etchant_data = comparison_data.copy()

            etchant_data["Etching Rate (um/min)"] = (
                etchant_data["Thickness Removed (μm)"]
                / etchant_data["Etching Time (min)"]
            )

            etchant_chart = etchant_data.pivot_table(
                index="Temperature (°C)",
                columns="Etchant",
                values="Etching Rate (um/min)",
                aggfunc="mean"
            )

            etchant_chart = etchant_chart.sort_index()

            fig2, ax2 = plt.subplots()

            for etchant_name in etchant_chart.columns:
                ax2.plot(
                    etchant_chart.index,
                    etchant_chart[etchant_name],
                    marker="o",
                    label=etchant_name
                )

            ax2.set_xlabel(
                "Temperature (°C)"
            )

            ax2.set_ylabel(
                "Etching Rate (um/min)"
            )

            ax2.set_title(
                "Etchant Comparison"
            )

            ax2.legend()

            fig2.tight_layout()

            fig2.savefig(
                etchant_plot_buffer,
                format="png",
                dpi=200
            )

            plt.close(fig2)

            etchant_plot_buffer.seek(0)

            pdf.showPage()

            pdf.setFont(
                "Helvetica-Bold",
                18
            )

            pdf.drawString(
                2 * cm,
                height - 2 * cm,
                "Etchant Comparison"
            )

            pdf.drawImage(
                ImageReader(etchant_plot_buffer),
                2 * cm,
                height - 15 * cm,
                width=17 * cm,
                height=10 * cm,
                preserveAspectRatio=True,
                anchor="c"
            )
            # =========================
            # PAGE 4 - Wafer Orientation Comparison
            # =========================

            orientation_plot_buffer = io.BytesIO()

            orientation_data = comparison_data.copy()

            orientation_data["Etching Rate (um/min)"] = (
                orientation_data["Thickness Removed (μm)"]
                / orientation_data["Etching Time (min)"]
            )

            orientation_chart_pdf = orientation_data.pivot_table(
                index="Temperature (°C)",
                columns="Wafer Orientation",
                values="Etching Rate (um/min)",
                aggfunc="mean"
            )

            orientation_chart_pdf = (
                orientation_chart_pdf.sort_index()
            )

            fig3, ax3 = plt.subplots()

            for orientation_name in orientation_chart_pdf.columns:
                ax3.plot(
                    orientation_chart_pdf.index,
                    orientation_chart_pdf[orientation_name],
                    marker="o",
                    label=orientation_name
                )

            ax3.set_xlabel(
                "Temperature (°C)"
            )

            ax3.set_ylabel(
                "Etching Rate (um/min)"
            )

            ax3.set_title(
                "Wafer Orientation Comparison"
            )

            ax3.legend()

            fig3.tight_layout()

            fig3.savefig(
                orientation_plot_buffer,
                format="png",
                dpi=200
            )

            plt.close(fig3)

            orientation_plot_buffer.seek(0)

            pdf.showPage()

            pdf.setFont(
                "Helvetica-Bold",
                18
            )

            pdf.drawString(
                2 * cm,
                height - 2 * cm,
                "Wafer Orientation Comparison"
            )

            pdf.drawImage(
                ImageReader(orientation_plot_buffer),
                2 * cm,
                height - 15 * cm,
                width=17 * cm,
                height=10 * cm,
                preserveAspectRatio=True,
                anchor="c"
            )
            # =========================
            # PAGE 5 - Arrhenius Analysis
            # =========================

            arrhenius_plot_buffer = io.BytesIO()

            fig4, ax4 = plt.subplots()

            ax4.plot(
                x,
                y,
                marker="o"
            )

            ax4.set_xlabel("1/T (K⁻¹)")
            ax4.set_ylabel("ln(Etching Rate)")
            ax4.set_title("Arrhenius Plot")

            fig4.tight_layout()

            fig4.savefig(
                arrhenius_plot_buffer,
                format="png",
                dpi=200
            )

            plt.close(fig4)

            arrhenius_plot_buffer.seek(0)

            pdf.showPage()

            pdf.setFont("Helvetica-Bold", 18)

            pdf.drawString(
                2 * cm,
                height - 2 * cm,
                "Arrhenius Analysis"
            )

            pdf.drawString(
                2 * cm,
                height - 3.5 * cm,
                f"Activation Energy: {activation_energy_kj:.2f} kJ/mol"
            )

            pdf.drawString(
                2 * cm,
                height - 4.5 * cm,
                f"R²: {r_squared:.4f}"
            )

            pdf.drawImage(
                ImageReader(arrhenius_plot_buffer),
                2 * cm,
                height - 15 * cm,
                width=17 * cm,
                height=10 * cm,
                preserveAspectRatio=True,
                anchor="c"
            )
            # Finish PDF
            pdf.save()

            pdf_buffer.seek(0)

            st.download_button(
                label="Download PDF Report",
                data=pdf_buffer,
                file_name="silicon_etching_report.pdf",
                mime="application/pdf"
            )
        else:

            st.warning(
                "No experimental data matches "
                "the selected conditions."
            )

    else:

        st.info(
            "The uploaded CSV does not contain "
            "the required columns for comparison."
        )

else:

    st.info(
        "Upload a CSV file above to use "
        "Condition Comparison."
    )

# =========================================================
# Manual Experimental Data
# =========================================================

st.subheader("Manual Experimental Data")

manual_data = pd.DataFrame({
    "Temperature (°C)": [60.0, 70.0, 80.0, 90.0],
    "Initial Thickness (μm)": [500.0, 500.0, 500.0, 500.0],
    "Final Thickness (μm)": [480.0, 465.0, 450.0, 430.0],
    "Etching Time (min)": [10.0, 10.0, 10.0, 10.0],
    "Etchant": ["KOH", "KOH", "KOH", "KOH"],
    "Wafer Orientation": ["(100)", "(100)", "(100)", "(100)"]
})

edited_data = st.data_editor(
    manual_data,
    num_rows="dynamic",
    width="stretch"
)

if st.button("Analyze Manual Data"):

    analysis_data = edited_data.copy()

    analysis_data["Thickness Removed (μm)"] = (
        analysis_data["Initial Thickness (μm)"]
        - analysis_data["Final Thickness (μm)"]
    )

    analysis_data["Etching Rate (μm/min)"] = (
        analysis_data["Thickness Removed (μm)"]
        / analysis_data["Etching Time (min)"]
    )

    if (
        analysis_data["Thickness Removed (μm)"] < 0
    ).any():

        st.error(
            "Error: Final thickness cannot be greater "
            "than initial thickness."
        )

    elif (
        analysis_data["Etching Time (min)"] <= 0
    ).any():

        st.error(
            "Error: Etching time must be greater than zero."
        )

    else:

        st.success(
            "Manual data analyzed successfully."
        )

        st.subheader(
            "Manual Analysis Results"
        )

        st.dataframe(
            analysis_data,
            width="stretch"
        )

        average_rate = (
            analysis_data[
                "Etching Rate (μm/min)"
            ].mean()
        )

        maximum_rate = (
            analysis_data[
                "Etching Rate (μm/min)"
            ].max()
        )

        minimum_rate = (
            analysis_data[
                "Etching Rate (μm/min)"
            ].min()
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Average Rate",
                f"{average_rate:.2f} μm/min"
            )

        with col2:
            st.metric(
                "Maximum Rate",
                f"{maximum_rate:.2f} μm/min"
            )

        with col3:
            st.metric(
                "Minimum Rate",
                f"{minimum_rate:.2f} μm/min"
            )

        st.subheader(
            "Etching Rate vs. Temperature"
        )

        chart_data = analysis_data[
            [
                "Temperature (°C)",
                "Etching Rate (μm/min)"
            ]
        ].copy()

        chart_data = chart_data.sort_values(
            "Temperature (°C)"
        )

        chart_data = chart_data.set_index(
            "Temperature (°C)"
        )

        st.line_chart(
            chart_data
        )


# =========================================================
# Formula
# =========================================================

st.divider()

st.subheader("Etching Rate Equation")

st.latex(
    r"""
    R = \frac{d_i-d_f}{t}
    """
)

st.write(
    "Where R is the silicon etching rate, "
    "di is the initial thickness, "
    "df is the final thickness, and "
    "t is the etching time."
)