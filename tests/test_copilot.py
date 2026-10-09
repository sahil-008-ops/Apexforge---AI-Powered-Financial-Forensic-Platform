import pytest
from apexforge.copilot.ca_copilot import CAInvestigationCopilot


def test_ca_copilot_query():
    copilot = CAInvestigationCopilot()
    res1 = copilot.query("Explain CGST Sec 16(2) ITC disallowance for circular trading")
    assert "CGST Act 2017" in res1["answer"]
    assert "Sec 16(2)" in res1["answer"]

    res2 = copilot.query("What are the rules for cash payments u/s 40A(3)?")
    assert "40A(3)" in res2["answer"]
    assert "₹10,000" in res2["answer"]

    res3 = copilot.query("Tell me about AIS unreported income u/s 68")
    assert "Sec 68" in res3["answer"]
