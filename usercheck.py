import pandas as pd
from flask import Flask, request, render_template
from datetime import datetime
import os
import io

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
        # file.save('./Files/'+file.filename)
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        print(file.filename)
        # df = pd.read_csv(file.filename)
        # df = pd.read_csv('./Files/'+file.filename) OLD LOGIC COMMENTED - JUN 10 DAX
        df = pd.read_csv(stream)
        
        print('---------------- New calculation ------------------')

        debit_sum = df.loc[df['transanctionRelatedType'].isin(['EntryFee', 'Withdrawal','Admin Deduction','Admin Credit']) & (df['transactionStatus'].isin(['Success','Pending'])), 'amount'].sum()
        credit_sum = df.loc[df['transanctionRelatedType'].isin(['Signup Bonus', 'Credit', 'Winnings', 'Refund']) & (df['transactionStatus'] == 'Success'), 'amount'].sum()
        print('Debit Sum - :',debit_sum)
        print('Credit Sum - :',credit_sum)
        print('Difference - :',format(credit_sum - debit_sum, ".2f") )
        difference = credit_sum - debit_sum

        # Extend winnings and refund info with additional columns
        # Count occurrences of each contestId where transanctionRelatedType is 'Winnings'
        contest_id_counts = df[df['transanctionRelatedType'].isin(['Winnings', 'Refund','EntryFee'])]['contestId'].value_counts().to_dict()
        contest_id_winRef_counts = df[df['transanctionRelatedType'].isin(['Winnings', 'Refund'])]['contestId'].value_counts().to_dict()
        contest_id_enf_counts = df[df['transanctionRelatedType'] == "EntryFee"]['contestId'].value_counts().to_dict()

        winnings_info = []
        refund_info = []
        Withdrawal_info = []
        credit_info =[]
        error_info = []

        # Winning
        for index, row in df[df['transanctionRelatedType'] == 'Winnings'].iterrows(): 

            enf_count = contest_id_enf_counts.get(row['contestId'], 0)
            win_ref_count = contest_id_winRef_counts.get(row['contestId'], 0)


            if enf_count >= win_ref_count:
                winnings_info.append({
                                        'link': "https://admin.americandream11.us/reports/ContestReport/" + str(row['contestId']),
                                        'amount': row['amount'],
                                        'contest_id': row['contestId'],
                                        'transaction_type': row['transanctionRelatedType'],
                                        'transaction_time': datetime.strptime(row['transanctionTime'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%m/%d/%Y'),
                                        'fixture_display_name': row['fixtureDisplayName'],
                                        'contest_name': row['contestName'],
                                        'fixture_start_date': datetime.strptime(row['fixtureStartDate'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%m/%d/%Y'),
                                        'total_count': contest_id_counts.get(row['contestId'], 0),
                                        'Win_Ref_count': win_ref_count,
                                        'EntryFee_count': enf_count
                                    } )
            else:
                print('error_message',f"Contest ID {row['contestId']} has more winnings/refund entries ({win_ref_count}) than entry fees ({enf_count}).")
                error_info.append({"error_message": f"Contest ID {row['contestId']} has more winnings/refund entries ({win_ref_count}) than entry fees ({enf_count})."})

        # Refund
        for index, row in df[df['transanctionRelatedType'] == 'Refund'].iterrows(): 

            enf_count = contest_id_enf_counts.get(row['contestId'], 0)
            win_ref_count = contest_id_winRef_counts.get(row['contestId'], 0)


            if enf_count >= win_ref_count:
                refund_info.append({
                                    'link': "https://admin.americandream11.us/reports/ContestReport/" + str(row['contestId']),
                                    'amount': row['amount'],
                                    'contest_id': row['contestId'],
                                    'transaction_type': row['transanctionRelatedType'],
                                    'transaction_time': datetime.strptime(row['transanctionTime'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%m/%d/%Y'),
                                    'fixture_display_name': row['fixtureDisplayName'],
                                    'contest_name': row['contestName'],
                                    'fixture_start_date': row['fixtureStartDate'],
                                    'total_count': contest_id_counts.get(row['contestId'], 0),
                                    'Win_Ref_count': win_ref_count,
                                    'EntryFee_count': enf_count
                                } )
            else:
                error_info.append({"error_message": f"Contest ID {row['contestId']} has more winnings/refund entries ({win_ref_count}) than entry fees ({enf_count})."})

        #Withdrawal
        for index, row in df[df['transanctionRelatedType'] == 'Withdrawal'].iterrows(): 

            if row['transactionStatus'] == 'Success' : # or row['transactionStatus'] ==  'Pending'
                Withdrawal_info.append({
                                    
                                    'amount': row['amount'],
                                    'transaction_type': row['transanctionRelatedType'],
                                    'transaction_time': datetime.strptime(row['transanctionTime'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%m/%d/%Y'),
                                    'transaction_status' : row['transactionStatus']
                                } )
            #else:
                # error_info.append({"error_message": f"Amount of {row['amount']} withdrwal has failed on .{datetime.strptime(row['transanctionTime'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%m/%d/%Y')}"})

        #Deposit

        for index, row in df[df['transanctionRelatedType'] == 'Credit'].iterrows(): 
            credit_info.append({
                  'amount': row['amount'],
                  'transaction_type': row['transanctionRelatedType'],
                  'transaction_time': datetime.strptime(row['transanctionTime'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%m/%d/%Y'),
                  'transaction_status' : row['transactionStatus']
            })
        
        Withdrawal_info = sorted(Withdrawal_info, key=lambda x: datetime.strptime(x['transaction_time'], '%m/%d/%Y'), reverse=True)
        latest_withdrawal_date = ""
        if Withdrawal_info:
            latest_withdrawal = Withdrawal_info[0]
            latest_withdrawal_date = datetime.strptime(latest_withdrawal['transaction_time'], '%m/%d/%Y')
        # else:
        #     latest_withdrawal_date = "No withdrawals"

        # Desc order with Date
        # Sorting winnings_info and refund_info
        winnings_info = sorted(winnings_info, key=lambda x: datetime.strptime(x['transaction_time'], '%m/%d/%Y'), reverse=True)
        if latest_withdrawal_date != "":
         winnings_info = [entry for entry in winnings_info if datetime.strptime(entry['transaction_time'], '%m/%d/%Y') >= latest_withdrawal_date]
        
        refund_info = sorted(refund_info, key=lambda x: datetime.strptime(x['transaction_time'], '%m/%d/%Y'), reverse=True)
        if latest_withdrawal_date != "":
         refund_info = [entry for entry in refund_info if datetime.strptime(entry['transaction_time'], '%m/%d/%Y') >= latest_withdrawal_date]

        Withdrawal_info = sorted(Withdrawal_info, key=lambda x: datetime.strptime(x['transaction_time'], '%m/%d/%Y'), reverse=True)


        resultObj = {
            'debit_sum': debit_sum,
            'credit_sum': credit_sum,
            'difference': difference,
            'winnings_info': winnings_info,
            'refund_info': refund_info,
            'Withdrawal_info' : Withdrawal_info,
            'latest_withdrawal_date' : latest_withdrawal_date,
            'credit_info' : credit_info,
            'validation_errors' : error_info
        }
        # results.to_csv('results.csv', index=False)

        # os.remove('./Files/'+file.filename)

        return render_template('result.html', **resultObj )
    

@app.route('/result', methods = ['POST','GET'])
def result():
    print('after file called')
    

if __name__ == '__main__':
    print('triggred')
    app.run(debug=True)

