import pandas as pd
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def index():
    print('test run for load')
    return render_template('upload.html')

@app.route('/upload', methods = ['POST','GET'])

def upload():
    if request.method == "POST" :
        print('file upload called')
        file = request.files['file']
        #file.save(file.filename)
        file.save('./Files/'+file.filename)
        print(file.filename)
        # df = pd.read_csv(file.filename)
        df = pd.read_csv('./Files/'+file.filename)
        
        print('---------------- New calculation ------------------')

        debit_sum = df.loc[df['transanctionRelatedType'].isin(['EntryFee', 'Withdrawal']) & (df['transactionStatus'].isin(['Success','Pending'])), 'amount'].sum()
        credit_sum = df.loc[df['transanctionRelatedType'].isin(['Signup Bonus', 'Credit', 'Winnings', 'Refund']) & (df['transactionStatus'] == 'Success'), 'amount'].sum()
        print('Debit Sum - :',debit_sum)
        print('Credit Sum - :',credit_sum)
        print('Difference - :',format(credit_sum - debit_sum, ".2f") )
        difference = credit_sum - debit_sum

        # new logic for the contestids
        validation_errors = []
        winnings_links = []
        valid_contest_ids = df[df['transanctionRelatedType'].isin(['Refund', 'Winnings'])]
        print("hiiiiiiiiiiiiiiiiii")
        contest_counts = valid_contest_ids['contestId'].value_counts()
        print('valid_contest_ids- :\n',valid_contest_ids)
        print('contest_counts - :',contest_counts)

        for contest_id, count in contest_counts.items():
            print('contest_id : ',contest_id)
            print('count : ',count)
            print('Contest id repeatation -',df['contestId'].value_counts().get(contest_id))
            # if count != 2 and df[(df['contestId'] == contest_id) & (df['transanctionRelatedType'].isin(['Refund', 'Winnings']))].any():
            if df['contestId'].value_counts().get(contest_id) != 2:
                validation_errors.append(f"Contest ID {contest_id} does not appear exactly twice as required.")
                
            elif df['contestId'].value_counts().get(contest_id) == 2:
                # winnings_df = df[df['transanctionRelatedType'] == 'Winnings']
                winnings_links.append("https://admin.americandream11.us/reports/ContestReport/" + str(contest_id))
                print('winnings_links : ',winnings_links)
        
        # Generate links for winnings
        # winnings_df = df[df['transanctionRelatedType'] == 'Winnings']
        # winnings_links = ["https://admin.americandream11.us/reports/ContestReport/" + str(id) for id in winnings_df['contestId']]
        

        # Save results
        # results = pd.DataFrame({
        #     'Debit Sum': [debit_sum],
        #     'Credit Sum': [credit_sum],
        #     'Difference': [difference]
        # })

        resultObj = {
            'debit_sum': debit_sum,
            'credit_sum': credit_sum,
            'difference': difference,
            'validation_errors': validation_errors,
            'winnings_links': winnings_links
        }

        # results.to_csv('results.csv', index=False)

        
        return render_template('result.html', **resultObj )
    

@app.route('/result', methods = ['POST','GET'])
def result():
    print('after file called')
    

if __name__ == '__main__':
    print('triggred')
    app.run(debug=True)







