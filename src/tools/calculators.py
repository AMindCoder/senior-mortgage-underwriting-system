from langchain.tools import tool


@tool
def calculate_dti_ratio(monthly_debt: float, monthly_income: float) -> str:
    """Calculate Debt-to-Income ratio.

    Args:
        monthly_debt: Total monthly debt obligations.
        monthly_income: Total monthly gross income.

    Returns:
        Formatted DTI ratio result.
    """
    if monthly_income <= 0:
        return "Error: Monthly income must be greater than 0"

    dti = (monthly_debt / monthly_income) * 100

    status = "Acceptable" if dti <= 43 else "High" if dti <= 50 else "Excessive"

    return (
        f"DTI Ratio: {dti:.2f}% ({status}) "
        f"- Debt: ${monthly_debt:,.2f}, Income: ${monthly_income:,.2f}"
    )


@tool
def calculate_ltv_ratio(loan_amount: float, property_value: float) -> str:
    """Calculate Loan-to-Value ratio.

    Args:
        loan_amount: The loan amount requested.
        property_value: Appraised value of the property.

    Returns:
        Formatted LTV ratio result.
    """
    if property_value <= 0:
        return "Error: Property value must be greater than 0"

    ltv = (loan_amount / property_value) * 100

    if ltv <= 80:
        status = "Excellent"
    elif ltv <= 90:
        status = "Good"
    elif ltv <= 97:
        status = "High"
    else:
        status = "Excessive"

    return (
        f"LTV Ratio: {ltv:.2f}% ({status}) "
        f"- Loan: ${loan_amount:,.2f}, Value: ${property_value:,.2f}"
    )


@tool
def calculate_reserves(
    liquid_assets: float, monthly_payment: float, required_months: int = 2
) -> str:
    """Calculate reserve coverage in months.

    Args:
        liquid_assets: Total liquid assets available.
        monthly_payment: Monthly PITI payment.
        required_months: Number of months reserves required (default 2).

    Returns:
        Formatted reserves analysis.
    """
    if monthly_payment <= 0:
        return "Error: Monthly payment must be greater than 0"

    months_coverage = liquid_assets / monthly_payment
    required_amount = monthly_payment * required_months
    status = "Adequate" if months_coverage >= required_months else "Insufficient"

    return (
        f"Reserves: {months_coverage:.1f} months coverage ({status}) "
        f"- Assets: ${liquid_assets:,.2f}, Required: ${required_amount:,.2f}"
    )


@tool
def calculate_housing_expense_ratio(monthly_payment: float, monthly_income: float) -> str:
    """Calculate housing expense ratio (front-end ratio).

    Args:
        monthly_payment: Monthly PITI payment.
        monthly_income: Total monthly gross income.

    Returns:
        Formatted housing expense ratio.
    """
    if monthly_income <= 0:
        return "Error: Monthly income must be greater than 0"

    ratio = (monthly_payment / monthly_income) * 100
    status = "Acceptable" if ratio <= 28 else "Elevated" if ratio <= 35 else "High"

    return (
        f"Housing Ratio: {ratio:.2f}% ({status}) "
        f"- Payment: ${monthly_payment:,.2f}, Income: ${monthly_income:,.2f}"
    )


@tool
def check_credit_score_policy(credit_score: int) -> str:
    """Check if credit score meets policy requirements.

    Args:
        credit_score: Borrower's credit score.

    Returns:
        Policy compliance result.
    """
    if credit_score >= 740:
        tier, adj = "Excellent", "Best rates available"
    elif credit_score >= 700:
        tier, adj = "Very Good", "Favorable rates"
    elif credit_score >= 660:
        tier, adj = "Good", "Standard rates"
    elif credit_score >= 620:
        tier, adj = "Fair", "Higher rates, may require compensating factors"
    else:
        tier, adj = "Below Minimum", "Does not meet conventional loan requirements"

    return f"Credit Score: {credit_score} - Tier: {tier} - {adj}"


@tool
def check_large_deposits(deposits: list, monthly_income: float) -> str:
    """Identify large deposits requiring sourcing documentation.

    Args:
        deposits: List of recent deposits [{'amount': float, 'date': str}, ...].
        monthly_income: Monthly income for threshold calculation.

    Returns:
        Analysis of deposits requiring documentation.
    """
    threshold = monthly_income * 0.25
    large_deposits = []

    for deposit in deposits:
        amount = deposit.get("amount", 0)
        if amount >= threshold:
            large_deposits.append(
                {"amount": amount, "date": deposit.get("date", "Unknown")}
            )

    if not large_deposits:
        return (
            f"No large deposits identified (threshold: ${threshold:,.2f}). "
            "All deposits are acceptable."
        )

    result = (
        f"Found {len(large_deposits)} large deposit(s) requiring documentation "
        f"(threshold: ${threshold:,.2f}):\n"
    )
    for i, dep in enumerate(large_deposits, 1):
        result += f"  {i}. ${dep['amount']:,.2f} on {dep['date']} - Sourcing documentation required\n"

    return result


@tool
def calculate_total_debt_obligations(debts: dict, proposed_payment: float) -> str:
    """Calculate total monthly debt obligations including proposed loan.

    Args:
        debts: Dictionary of current debts {'debt_name': amount, ...}.
        proposed_payment: Proposed monthly loan payment.

    Returns:
        Total debt calculation.
    """
    current_debt = sum(debts.values())
    total_obligation = current_debt + proposed_payment

    breakdown = "\n".join([f"  - {k}: ${v:,.2f}" for k, v in debts.items()])

    return (
        f"Total Monthly Obligations: ${total_obligation:,.2f}\n"
        f"Current Debt: ${current_debt:,.2f}\n"
        f"{breakdown}\n"
        f"Proposed Payment: ${proposed_payment:,.2f}"
    )
