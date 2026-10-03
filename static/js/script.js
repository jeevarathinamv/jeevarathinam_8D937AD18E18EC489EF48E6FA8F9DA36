// Custom JavaScript for College Entrepreneurship Idea Submission Portal

document.addEventListener('DOMContentLoaded', function () {

  // Auto-calculate Evaluation Score in evaluate_idea.html
  const innovationInput = document.getElementById('innovation_score');
  const feasibilityInput = document.getElementById('feasibility_score');
  const marketInput = document.getElementById('market_potential_score');
  const socialInput = document.getElementById('social_impact_score');
  const totalDisplay = document.getElementById('total_score_display');
  const totalInput = document.getElementById('total_score_input');

  function calculateTotalScore() {
    if (innovationInput && feasibilityInput && marketInput && socialInput) {
      const v1 = parseInt(innovationInput.value) || 0;
      const v2 = parseInt(feasibilityInput.value) || 0;
      const v3 = parseInt(marketInput.value) || 0;
      const v4 = parseInt(socialInput.value) || 0;

      const total = v1 + v2 + v3 + v4;

      if (totalDisplay) {
        totalDisplay.textContent = total;
      }
      if (totalInput) {
        totalInput.value = total;
      }
    }
  }

  if (innovationInput && feasibilityInput && marketInput && socialInput) {
    [innovationInput, feasibilityInput, marketInput, socialInput].forEach(input => {
      input.addEventListener('input', calculateTotalScore);
      input.addEventListener('change', calculateTotalScore);
    });
    calculateTotalScore();
  }

  // Form Validation
  const forms = document.querySelectorAll('.needs-validation');
  Array.from(forms).forEach(function (form) {
    form.addEventListener('submit', function (event) {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      form.classList.add('was-validated');
    }, false);
  });

});
