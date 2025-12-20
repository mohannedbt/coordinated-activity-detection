namespace Behavior_risk_UI.Models;
public class DashboardViewModel
{
    // KPIs (top cards)
    public int TotalPosts { get; set; }
    public int AutoActions { get; set; }
    public int QueueReviews { get; set; }
    public double AvgRisk { get; set; }
    public string SummaryJson { get; set; }   // raw JSON for charts
    public string PostsJson { get; set; }   
    // Charts
    public Dictionary<string, int> DecisionCounts { get; set; }
    public Dictionary<string, int> ReasonCounts { get; set; }

    // Tables
    public List<PostCardViewModel> TopRiskPosts { get; set; }
    public List<AccountDto> TopAccounts { get; set; } = new();
    public string AccountsJson { get; set; }
}

public class PostCardViewModel
{
    public int PostId { get; set; }
    public string Text { get; set; }
    public double RiskScore { get; set; }
    public double Confidence { get; set; }
    public string Decision { get; set; }
    public string Interpretation { get; set; }
    
}

