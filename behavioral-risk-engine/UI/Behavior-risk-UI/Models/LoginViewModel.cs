namespace Behavior_risk_UI.Models;

using System.ComponentModel.DataAnnotations;


public class LoginViewModel
    {
        [Required]
        public string Username { get; set; } = "";

        [Required]
        [DataType(DataType.Password)]
        public string Password { get; set; } = "";

        public string? Error { get; set; }
    }

