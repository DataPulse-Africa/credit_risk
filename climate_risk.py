import streamlit as st
import pandas as pd
import numpy as np
import json
from typing import Dict, List, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ClimateRiskScreeningTool:
    def __init__(self):
        # Initialize ESG Exclusion List
        self.esg_exclusion_list = {
            'fossil_fuels': ['coal_mining', 'oil_gas_extraction', 'fossil_power_generation'],
            'controversial_weapons': ['cluster_munitions', 'landmines', 'nuclear_weapons'],
            'ethical_concerns': ['tobacco', 'gambling', 'adult_entertainment'],
            'environmental_violations': ['deforestation', 'high_emission_operations']
        }
        
        # Define climate risk factors and weights
        self.climate_risk_factors = {
            'physical_risk': {
                'flood_risk': 0.25,
                'heat_stress': 0.20,
                'sea_level_rise': 0.15,
                'wildfire_risk': 0.15
            },
            'transition_risk': {
                'carbon_price_exposure': 0.25,
                'regulatory_compliance': 0.20,
                'technology_disruption': 0.15
            }
        }

    def load_company_data(self, company_data: Dict) -> pd.DataFrame:
        """Load and validate company data."""
        try:
            df = pd.DataFrame([company_data])
            required_columns = ['company_name', 'industry', 'location', 'revenue', 
                              'carbon_footprint', 'physical_risk_score', 
                              'transition_risk_score']
            if not all(col in df.columns for col in required_columns):
                raise ValueError("Missing required columns in company data")
            return df
        except Exception as e:
            logger.error(f"Error loading company data: {str(e)}")
            raise

    def screen_esg_exclusions(self, company_data: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Screen company against ESG exclusion list."""
        violations = []
        company_industry = company_data['industry'].iloc[0].lower()
        
        for category, industries in self.esg_exclusion_list.items():
            if any(industry in company_industry for industry in industries):
                violations.append(category)
        
        return len(violations) == 0, violations

    def calculate_climate_risk_score(self, company_data: pd.DataFrame) -> float:
        """Calculate weighted climate risk score."""
        try:
            physical_score = sum(
                company_data[f"{factor}_score"].iloc[0] * weight 
                for factor, weight in self.climate_risk_factors['physical_risk'].items()
            )
            transition_score = sum(
                company_data[f"{factor}_score"].iloc[0] * weight 
                for factor, weight in self.climate_risk_factors['transition_risk'].items()
            )
            return 0.6 * physical_score + 0.4 * transition_score
        except Exception as e:
            logger.error(f"Error calculating climate risk score: {str(e)}")
            return 0.0

    def identify_esg_risks(self, company_data: pd.DataFrame) -> List[str]:
        """Identify specific ESG risks based on thresholds."""
        risks = []
        
        if company_data['carbon_footprint'].iloc[0] / company_data['revenue'].iloc[0] > 100:
            risks.append("High carbon intensity")
        
        if company_data['physical_risk_score'].iloc[0] > 7:
            risks.append("High physical climate risk")
            
        if company_data['transition_risk_score'].iloc[0] > 6:
            risks.append("High transition risk")
            
        return risks

    def assess_opportunities(self, company_data: pd.DataFrame) -> List[str]:
        """Identify climate-related opportunities."""
        opportunities = []
        
        if 'renewable' in company_data['industry'].iloc[0].lower():
            opportunities.append("Renewable energy market growth")
        if company_data['carbon_footprint'].iloc[0] / company_data['revenue'].iloc[0] < 50:
            opportunities.append("Low-carbon competitive advantage")
        if 'green' in company_data['industry'].iloc[0].lower():
            opportunities.append("Green technology innovation")
            
        return opportunities

    def generate_report(self, company_data: Dict) -> Dict:
        """Generate comprehensive climate risk report."""
        try:
            df = self.load_company_data(company_data)
            
            esg_compliant, esg_violations = self.screen_esg_exclusions(df)
            climate_risk_score = self.calculate_climate_risk_score(df)
            esg_risks = self.identify_esg_risks(df)
            opportunities = self.assess_opportunities(df)
            
            report = {
                'company_name': df['company_name'].iloc[0],
                'esg_compliant': esg_compliant,
                'esg_violations': esg_violations,
                'climate_risk_score': round(climate_risk_score, 2),
                'esg_risks': esg_risks,
                'climate_opportunities': opportunities,
                'recommendation': self._generate_recommendation(esg_compliant, climate_risk_score)
            }
            
            logger.info(f"Report generated for {report['company_name']}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return {}

    def _generate_recommendation(self, esg_compliant: bool, climate_risk_score: float) -> str:
        """Generate investment recommendation based on screening results."""
        if not esg_compliant:
            return "Do not proceed - ESG exclusion list violations detected"
        if climate_risk_score > 8:
            return "High risk - requires detailed due diligence"
        elif climate_risk_score > 5:
            return "Moderate risk - proceed with caution"
        else:
            return "Low risk - suitable for investment consideration"

# Streamlit App
st.title("Climate Risk Pre-Screening Tool")
st.markdown("Enter company details to assess climate risks, ESG compliance, and opportunities.")

# Input form
with st.form("company_form"):
    st.subheader("Company Information")
    company_name = st.text_input("Company Name", value="GreenTech Solutions")
    industry = st.text_input("Industry", value="Renewable Energy")
    location = st.text_input("Location", value="California")
    revenue = st.number_input("Revenue (USD)", min_value=0.0, value=100000000.0, step=1000000.0)
    carbon_footprint = st.number_input("Carbon Footprint (tons CO2e)", min_value=0.0, value=2000000.0, step=10000.0)

    st.subheader("Risk Scores (0-10)")
    physical_risk_score = st.slider("Physical Risk Score", 0.0, 10.0, 4.5)
    transition_risk_score = st.slider("Transition Risk Score", 0.0, 10.0, 3.2)
    flood_risk_score = st.slider("Flood Risk Score", 0.0, 10.0, 5.0)
    heat_stress_score = st.slider("Heat Stress Score", 0.0, 10.0, 4.0)
    sea_level_rise_score = st.slider("Sea Level Rise Score", 0.0, 10.0, 3.5)
    wildfire_risk_score = st.slider("Wildfire Risk Score", 0.0, 10.0, 5.0)
    carbon_price_exposure_score = st.slider("Carbon Price Exposure Score", 0.0, 10.0, 3.0)
    regulatory_compliance_score = st.slider("Regulatory Compliance Score", 0.0, 10.0, 3.5)
    technology_disruption_score = st.slider("Technology Disruption Score", 0.0, 10.0, 3.0)

    submitted = st.form_submit_button("Generate Report")

# Process form submission
if submitted:
    company_data = {
        'company_name': company_name,
        'industry': industry,
        'location': location,
        'revenue': revenue,
        'carbon_footprint': carbon_footprint,
        'physical_risk_score': physical_risk_score,
        'transition_risk_score': transition_risk_score,
        'flood_risk_score': flood_risk_score,
        'heat_stress_score': heat_stress_score,
        'sea_level_rise_score': sea_level_rise_score,
        'wildfire_risk_score': wildfire_risk_score,
        'carbon_price_exposure_score': carbon_price_exposure_score,
        'regulatory_compliance_score': regulatory_compliance_score,
        'technology_disruption_score': technology_disruption_score
    }

    try:
        # Initialize tool and generate report
        tool = ClimateRiskScreeningTool()
        report = tool.generate_report(company_data)

        # Display report
        st.subheader("Climate Risk Screening Report")
        st.markdown(f"**Company Name**: {report['company_name']}")
        st.markdown(f"**ESG Compliant**: {'Yes' if report['esg_compliant'] else 'No'}")
        st.markdown(f"**ESG Violations**: {', '.join(report['esg_violations']) if report['esg_violations'] else 'None'}")
        st.markdown(f"**Climate Risk Score**: {report['climate_risk_score']}/10")
        st.markdown(f"**ESG Risks**: {', '.join(report['esg_risks']) if report['esg_risks'] else 'None'}")
        st.markdown(f"**Climate Opportunities**: {', '.join(report['climate_opportunities']) if report['climate_opportunities'] else 'None'}")
        st.markdown(f"**Recommendation**: {report['recommendation']}")

        # Option to download report as JSON
        st.download_button(
            label="Download Report (JSON)",
            data=json.dumps(report, indent=4),
            file_name=f"{report['company_name']}_climate_risk_report.json",
            mime="application/json"
        )
    except Exception as e:
        st.error(f"Error generating report: {str(e)}")