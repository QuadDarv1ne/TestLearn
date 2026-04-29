/**
 * Quiz functionality for TestLearn platform
 * Timer, question navigation, and answer handling
 */

const Quiz = {
    currentQuestionIndex: 0,
    answers: {},
    timeRemaining: 0,
    timerInterval: null,
    quizId: null,

    /**
     * Initialize quiz with data
     */
    init(quizData) {
        this.quizId = quizData.id;
        this.timeRemaining = quizData.time_limit || 900; // Default 15 minutes
        this.questions = quizData.questions || [];
        this.totalQuestions = this.questions.length;

        this.renderQuestions();
        this.showQuestion(0);
        this.startTimer();
        this.bindEvents();
    },

    /**
     * Render all questions (hidden initially)
     */
    renderQuestions() {
        const container = document.getElementById('quiz-questions-container');
        if (!container) return;

        container.innerHTML = this.questions.map((q, index) => `
            <div id="question-${index}" class="question-card hidden" data-question-index="${index}">
                <div class="mb-4">
                    <span class="text-sm font-medium text-gray-500">Вопрос ${index + 1} из ${this.totalQuestions}</span>
                    <h3 class="text-xl font-semibold mt-2">${this.escapeHtml(q.question_text)}</h3>
                </div>
                
                <div class="space-y-3">
                    ${this.renderOptions(q, index)}
                </div>
                
                <div class="mt-6 flex justify-between">
                    <button onclick="Quiz.prevQuestion()" 
                            class="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300 ${index === 0 ? 'opacity-50 cursor-not-allowed' : ''}"
                            ${index === 0 ? 'disabled' : ''}>
                        ← Назад
                    </button>
                    
                    ${index < this.totalQuestions - 1 ? 
                        `<button onclick="Quiz.nextQuestion()" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                            Далее →
                        </button>` :
                        `<button onclick="Quiz.submitQuiz()" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
                            Завершить тест
                        </button>`
                    }
                </div>
            </div>
        `).join('');
    },

    /**
     * Render answer options
     */
    renderOptions(question, questionIndex) {
        const options = [
            { key: 'A', text: question.option_a },
            { key: 'B', text: question.option_b },
            { key: 'C', text: question.option_c },
            { key: 'D', text: question.option_d }
        ];

        return options.map(opt => `
            <label class="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
                <input type="radio" 
                       name="question-${questionIndex}" 
                       value="${opt.key}"
                       class="w-4 h-4 text-blue-600"
                       onchange="Quiz.recordAnswer(${questionIndex}, '${opt.key}')">
                <span class="ml-3">${this.escapeHtml(opt.text)}</span>
            </label>
        `).join('');
    },

    /**
     * Show specific question
     */
    showQuestion(index) {
        // Hide all questions
        document.querySelectorAll('.question-card').forEach(card => {
            card.classList.add('hidden');
        });

        // Show current question
        const currentQuestion = document.getElementById(`question-${index}`);
        if (currentQuestion) {
            currentQuestion.classList.remove('hidden');
        }

        this.currentQuestionIndex = index;
        this.updateProgress();
    },

    /**
     * Go to next question
     */
    nextQuestion() {
        if (this.currentQuestionIndex < this.totalQuestions - 1) {
            this.showQuestion(this.currentQuestionIndex + 1);
        }
    },

    /**
     * Go to previous question
     */
    prevQuestion() {
        if (this.currentQuestionIndex > 0) {
            this.showQuestion(this.currentQuestionIndex - 1);
        }
    },

    /**
     * Record answer for a question
     */
    recordAnswer(questionIndex, answer) {
        this.answers[questionIndex] = answer;
        
        // Visual feedback
        const questionCard = document.getElementById(`question-${questionIndex}`);
        if (questionCard) {
            questionCard.classList.add('border-blue-200');
            setTimeout(() => {
                questionCard.classList.remove('border-blue-200');
            }, 300);
        }
    },

    /**
     * Update progress indicator
     */
    updateProgress() {
        const progressContainer = document.getElementById('quiz-progress');
        if (!progressContainer) return;

        const answered = Object.keys(this.answers).length;
        const percentage = Math.round((answered / this.totalQuestions) * 100);

        progressContainer.innerHTML = `
            <div class="flex justify-between text-sm text-gray-600 mb-2">
                <span>Вопрос ${this.currentQuestionIndex + 1} из ${this.totalQuestions}</span>
                <span>Ответили: ${answered}/${this.totalQuestions}</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                     style="width: ${percentage}%"></div>
            </div>
        `;
    },

    /**
     * Start countdown timer
     */
    startTimer() {
        const timerDisplay = document.getElementById('quiz-timer');
        if (!timerDisplay) return;

        this.timerInterval = setInterval(() => {
            this.timeRemaining--;
            
            const minutes = Math.floor(this.timeRemaining / 60);
            const seconds = this.timeRemaining % 60;
            
            timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            
            // Warning when time is running out
            if (this.timeRemaining <= 60) {
                timerDisplay.classList.add('text-red-600');
            } else if (this.timeRemaining <= 300) {
                timerDisplay.classList.add('text-yellow-600');
            }

            // Time's up
            if (this.timeRemaining <= 0) {
                this.stopTimer();
                Toast.warning('Время вышло! Отправляем ответы...');
                this.submitQuiz();
            }
        }, 1000);
    },

    /**
     * Stop countdown timer
     */
    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    },

    /**
     * Submit quiz and show results
     */
    async submitQuiz() {
        // Check if all questions are answered
        const unanswered = this.totalQuestions - Object.keys(this.answers).length;
        if (unanswered > 0 && !confirm(`Вы не ответили на ${unanswered} вопрос${this.getPlural(unanswered, 'ы', 'ы', 'ов')}. Продолжить?`)) {
            return;
        }

        this.stopTimer();
        Loading.show();

        try {
            // Calculate score
            let correctCount = 0;
            this.questions.forEach((q, index) => {
                if (this.answers[index] === q.correct_option) {
                    correctCount++;
                }
            });

            const score = correctCount;
            const total = this.totalQuestions;

            // Send to backend
            const result = await API.post('/api/quizzes/submit', {
                quiz_id: this.quizId,
                score: score,
                total: total,
                answers: this.answers
            });

            // Redirect to results page
            window.location.href = `/quiz/result/${result.id}`;
        } catch (error) {
            console.error('Quiz submission error:', error);
            Toast.error('Ошибка при отправке теста');
            Loading.hide();
        }
    },

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight') {
                this.nextQuestion();
            } else if (e.key === 'ArrowLeft') {
                this.prevQuestion();
            }
        });

        // Prevent accidental navigation
        window.addEventListener('beforeunload', (e) => {
            if (Object.keys(this.answers).length > 0) {
                e.preventDefault();
                e.returnValue = '';
            }
        });
    },

    /**
     * Helper: escape HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    /**
     * Helper: get plural form
     */
    getPlural(noun, singular, dual, plural) {
        const lastDigit = Math.abs(noun) % 10;
        const lastTwoDigits = Math.abs(noun) % 100;
        
        if (lastTwoDigits >= 11 && lastTwoDigits <= 19) return plural;
        if (lastDigit === 1) return singular;
        if (lastDigit >= 2 && lastDigit <= 4) return dual;
        return plural;
    }
};

// Export for use in other scripts
window.Quiz = Quiz;
