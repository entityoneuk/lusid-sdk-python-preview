import unittest
import requests
import json
import uuid
import os
from datetime import datetime, timedelta
from dateutil import parser
import pytz
import lusid
import lusid.models as models
from unittest import TestCase
from msrest.authentication import BasicTokenAuthentication
from api_client_builder import ApiClientBuilder

from InstrumentLoader import InstrumentLoader
import pandas as pd
import shrine
from shrine import models as shrine_models

import time


try:
    # Python 3.x
    from urllib.request import pathname2url
except ImportError:
    # Python 2.7
    from urllib import pathname2url


class TestAccessShrine(TestCase):
    client_admin = None
    client_super = None
    client_restricted = None

    shrine_client = None
    effective_date = datetime(2017, 1, 1, tzinfo=pytz.utc)


    @classmethod
    def setUpClass(cls):

        cls.ISIN_PROPERTY_KEY = "Instrument/default/Isin"
        cls.SEDOL_PROPERTY_KEY = "Instrument/default/Sedol"
        cls.TICKER_PROPERTY_KEY = "Instrument/default/Ticker"
        cls.FIGI_SCHEME = "Figi"
        cls.CUSTOM_INTERNAL_SCHEME = "ClientInternal"
        cls.GROUPBY_KEY = "Instrument/default/Name"
        cls.AGGREGATION_KEY = "Holding/default/PV"
        cls.INSTRUMENT_FILE = 'data/DOW Figis.csv'
        cls.sorted_instrument_ids = []
        cls.instrument_universe = {}

        # Load our multiple configuration details from the local secrets file
        dir_path = os.path.dirname(os.path.realpath(__file__))

        cls.client_super = ApiClientBuilder().build("secretsprod.json")

        user_list = {"restricted": cls.client_restricted,"administrator": cls.client_admin}

        # set up the APIs
        cls.instruments = lusid.InstrumentsApi(cls.client_super)
        cls.transaction_portfolios = lusid.TransactionPortfoliosApi(cls.client_super)
        cls.property_definitions = lusid.PropertyDefinitionsApi(cls.client_super)
        cls.portfolios = lusid.PortfoliosApi(cls.client_super)
        cls.analytic_stores = lusid.AnalyticsStoresApi(cls.client_super)
        cls.quote_store = lusid.QuotesApi(cls.client_super)
        cls.aggregation = lusid.AggregationApi(cls.client_super)
        cls.search = lusid.SearchApi(cls.client_super)


        # Do the same for Shrine - note the call is slightly different for now, with the token being passed in later
        shrine_url = 'https://shrine-am-ci.lusid.com'
        api_token = {"access_token": cls.client_super.configuration.access_token}
        cls.shrine_client = shrine.FINBOURNEShrineAPI(BasicTokenAuthentication(api_token), shrine_url)

        #cls.api_url = os.getenv("FBN_LUSID_API_URL", config["api"]["apiUrl"])

        # Create shrine and lusid clients, return credentials, using super who will be in charge
        # of creating policies and roles.
        #credentials = cls.create_shrine_lusid_clients(username_super, password_super, client_id, client_secret, token_url)

        ##################################
        # create scopes here
        # prettyprint.heading('Analyst Scope Code', analyst_scope_code)

        # Create scope
        uuid_gen = uuid.uuid4()
        scope = "Testdemo"
        analyst_scope_code = scope          # + "-" + str(uuid_gen)

        ################
        # Cut-down or full sized test?
        # Full-sized test runs from 1/1/17 to 31/12/18 (2 full years)
        # Short from 1/1/17 to 31/3/17 (3 months)

        close_file = 'data/Global Equity closes.csv'
        transactions_file = 'data/DJIItransactions_short.csv'
        cls.INSTRUMENT_FILE = 'data/GlobalEquityFigis.csv'
        transaction_portfolio_code = 'Global-Equity'
        fx_file = 'data/FXCloses.csv'
        termination_date = datetime(2017, 4, 4, tzinfo=pytz.utc)
        valuation_date = datetime(2019, 4, 15, tzinfo=pytz.utc)

        today_date = datetime(2019, 6, 7, tzinfo=pytz.utc)


        # credentials = cls.create_shrine_lusid_clients(username_default, password_default, client_id_default,client_secret_default, token_url)

        ##################################
        # Create and load in instruments - we would like to do this under restricted permissions but are awaiting
        # a new implemenation of complexIDpath from shrine

        inst_list = cls.load_instruments_from_file()
        cls.upsert_intruments(inst_list)

        # for_property = [model_for_spec]  # temporal restriction
        # Start the clock on timing
        start = time.time()

        end = time.time()
        print('Inst load: ' + str(end-start))

        ##################################
        # Create transactions portfolio
        # Define unique code for our portfolio

        # The date our portfolios were first created
        portfolio_creation_date = cls.effective_date

        # # Create the request to add our portfolio
        # transaction_portfolio_request = models.CreateTransactionPortfolioRequest(
        #     display_name=transaction_portfolio_code,
        #     code=transaction_portfolio_code,
        #     base_currency='USD',
        #     description='Paper transaction portfolio',
        #     created=portfolio_creation_date)
        #
        # # Call LUSID to create our portfolio
        # try:
        #     response = cls.portfolios.get_portfolio(scope=analyst_scope_code, code=transaction_portfolio_code)
        # except Exception as err_response:
        #     if err_response.status == 404:
        #         # portfolio does not exist, create.
        #         response = cls.transaction_portfolios.create_portfolio(scope=analyst_scope_code, create_request=transaction_portfolio_request)

        # Pretty print the response from LUSID
        # prettyprint.portfolio_response(portfolio_response)

        ##################################
        # Populating our analyst's portfolio with a starting cash balance

        # Set the date from which the cash balance will apply to be just after portfolio creation
        holdings_effective_date = cls.effective_date

        end = time.time()




        # We now need to add in closing prices for our instruments over the last two years
        # Import our instrument prices from a CSV file

        instrument_close_prices = pd.read_csv(close_file)

        end = time.time()
        print('close prices load: ' + str(end - start))

        # Pretty print our pricing
        # print(instrument_prices.head(n=10))

        # We can now store this information in LUSID in an analytics store.
        # Note we need a separate store for each closing date
        # Set our analytics effective dates

        analytics_store_dates = []      # we will need to populate this from the closing prices

        # Create prices via instrument, analytic
        instrument_quotes = []

        for index, row in instrument_close_prices.iterrows():

            instrument_id = row["Figi"]
            instrument_id_type = 'Figi'

            # luid = cls.search.instruments_search(
            #     symbols=[
            #         models.InstrumentSearchProperty(
            #             key='Instrument/default/{}'.format(instrument_id_type),
            #             value=instrument_id)
            #     ],
            #     mastered_only=True
            # )[0].mastered_instruments[0].identifiers['LusidInstrumentId'].value

            instrument_quotes.append(models.UpsertQuoteRequest(
                quote_id=models.QuoteId(
                    provider='DataScope',
                    price_source='',
                    instrument_id=row['Figi'],
                    instrument_id_type='Figi',
                    quote_type='Price',
                    price_side='Mid'),
                metric_value=models.MetricValue(
                    value=row['AdjClose'],
                    unit=row['Currency']),
                effective_at=parser.parse(row['Date']).replace(tzinfo=pytz.utc),
                lineage='InternalSystem'
            ))

        response = cls.quote_store.upsert_quotes(
            scope=analyst_scope_code,
            quotes=instrument_quotes)

        # Prepare an empty list to hold the quote requests
        fx_quote_requests = []
        fx_close_prices = pd.read_csv(fx_file)
        # Iterate over each FX rate
        for index, fx_rate in fx_close_prices.iterrows():
            # Add a quote for the FX rate
            fx_quote_requests.append(
                models.UpsertQuoteRequest(
                    quote_id=models.QuoteId(
                        provider='DataScope',
                        price_source='',
                        instrument_id=fx_rate['pair'],
                        instrument_id_type='CurrencyPair',
                        quote_type='Rate',
                        price_side='Mid'),
                    metric_value=models.MetricValue(
                        value=fx_rate['rate'],
                        unit='rate'),
                    effective_at=parser.parse(fx_rate['date']).replace(tzinfo=pytz.utc),
                    lineage='InternalSystem'))

            # Create the reverse pair name
            reverse_pair = '/'.join(fx_rate['pair'].split('/')[::-1])

            # Add a quote for the reverse FX rate
            fx_quote_requests.append(
                models.UpsertQuoteRequest(
                    quote_id=models.QuoteId(
                        provider='DataScope',
                        price_source='',
                        instrument_id=reverse_pair,
                        instrument_id_type='CurrencyPair',
                        quote_type='Rate',
                        price_side='Mid'),
                    metric_value=models.MetricValue(
                        value=1 / fx_rate['rate'],
                        unit='rate'),
                    effective_at=parser.parse(fx_rate['date']).replace(tzinfo=pytz.utc),
                    lineage='InternalSystem'))

        # Upsert the quotes into LUSID
        response = cls.quote_store.upsert_quotes(
            scope=analyst_scope_code,
            quotes=fx_quote_requests)

        print('Analytics Set')
        inline_recipe = models.ConfigurationRecipe(
            code='quotes_recipe',
            market=models.MarketContext(
                market_rules=[
                    models.MarketDataKeyRule(
                        key='Equity.Figi.*',
                        supplier='DataScope',
                        data_scope=analyst_scope_code,
                        quote_type='Price',
                        price_side='Mid'),
                    models.MarketDataKeyRule(
                        key='Equity.LusidInstrumentId.*',
                        supplier='DataScope',
                        data_scope=analyst_scope_code,
                        quote_type='Price',
                        price_side='Mid'),
                    models.MarketDataKeyRule(
                        key='Fx.CurrencyPair.*',
                        supplier='DataScope',
                        data_scope=analyst_scope_code,
                        quote_type='Rate',
                        price_side='Mid')
                ],
                suppliers=models.MarketContextSuppliers(
                    commodity='DataScope',
                    credit='DataScope',
                    equity='DataScope',
                    fx='DataScope',
                    rates='DataScope'),
                options=models.MarketOptions(
                    default_supplier='DataScope',
                    default_instrument_code_type='Figi',
                    default_scope=analyst_scope_code)
            )
        )

        aggregation_request = models.AggregationRequest(
            inline_recipe=inline_recipe,
            effective_at=valuation_date,
            metrics=[
                models.AggregateSpec(
                    key='Holding/default/SubHoldingKey',
                    op='Value'),
                models.AggregateSpec(
                    key='Holding/default/Units',
                    op='Sum'),
                models.AggregateSpec(
                    key='Holding/default/Cost',
                    op='Sum'),
                models.AggregateSpec(
                    key='Holding/default/PV',
                    op='Sum'),
                models.AggregateSpec(
                    key='Holding/default/Price',
                    op='Sum')
            ],
            group_by=[
                'Holding/default/SubHoldingKey'
            ])
        try:
            # Call LUSID to aggregate across all of our portfolios for 'valuation_date'
            aggregated_portfolio = cls.aggregation.get_aggregation_by_portfolio(
                scope=analyst_scope_code,
                code=transaction_portfolio_code,
                request=aggregation_request)

        except Exception as inst:
            if inst.error.status == 403:
                # entitlements rejects this, step to next date
                print("error")
            else:
                raise inst

        query_params = models.TransactionQueryParameters(
            start_date=cls.effective_date,
            end_date=today_date,
            query_mode='TradeDate',
            show_cancelled_transactions=None)

        transactions_response = cls.transaction_portfolios.build_transactions(
            scope=analyst_scope_code,
            code=transaction_portfolio_code,
            instrument_property_keys=['Instrument/default/Name'],
            parameters=query_params
        )


        exit()













        print('Tran portfolio: ' + str(end - start))
        ##################################
        # Allow our analysts to trade across their tradeable instrument universe
        # and add transactions to their transaction portfolio
        # Import transactions from DJII transactions. We have 30 instruments with hidden strategies to investigate

        djii_transactions = cls.load_transactions_from_file(transactions_file)

        end = time.time()

        print('Tran load from file: ' + str(end - start))

        # create the strategy property. Although strategies are currently set to none for all transactions,
        # this property is created to allow trades to be identified and categorised at a later date
        # Create a request to define our strategy property
        property_request = models.CreatePropertyDefinitionRequest(
            domain='Trade',
            scope=analyst_scope_code,
            code='strategy',
            value_required=False,
            display_name='strategy',
            data_type_id=models.ResourceId(
                scope='default',
                code='string')
            )

        # Call LUSID to create our property
        try:
            property_response = cls.property_definitions.get_property_definition(domain='Trade', scope=analyst_scope_code, code='strategy')
        except Exception as err_response:
            if err_response.error.status == 404:       #why is this different
                # property does not exist, create.
                property_response = cls.property_definitions.create_property_definition(definition=property_request)

        # Grab the key off the response to use when referencing this property in other LUSID calls
        strategy_property_key = property_response.key

        #'Trade/notepad-access-finbourne/strategy'
        # Pretty print our strategy property key
        # prettyprint.heading('Strategy Property Key: ', strategy_property_key)

        # Now we wish to upsert our trades into LUSID so we can start our analysis

        # Initialise a list to hold our transactions
        batch_transaction_requests = []

        # Iterate over the transactions for each portfolio
        for transaction_id, transaction in djii_transactions.items():

            if 'Cash' in transaction['instrument_name']:
                identifier_key = 'Instrument/default/Currency'
            else:
                identifier_key = 'Instrument/default/Figi'

            batch_transaction_requests.append(
                models.TransactionRequest(
                    transaction_id=transaction_id,
                    type=transaction['type'],
                    instrument_identifiers={
                        identifier_key: transaction['instrument_uid']},
                    transaction_date=transaction['transaction_date'],
                    settlement_date=transaction['settlement_date'],
                    units=transaction['units'],
                    transaction_price=models.TransactionPrice(
                        price=transaction['transaction_price'],
                        type='Price'),
                    total_consideration=models.CurrencyAndAmount(
                        amount=transaction['total_cost'],
                        currency=transaction['transaction_currency']),
                    source='Client',
                    transaction_currency=transaction['transaction_currency'],
                    properties={strategy_property_key: models.PropertyValue(label_value=transaction['strategy']),
                        "Trade/default/TradeToPortfolioRate": models.PropertyValue(metric_value=models.MetricValue(1.0))}
                ))
        end = time.time()
        print('batch tran create: ' + str(end - start))

        # properties = {
        #     strategy_property_key: models.PropertyValue(
        #         label_value=transaction['strategy']),
        #     'Trade/default/TradeToPortfolioRate': models.PropertyValue(
        #         metric_value=models.MetricValue(1.0))
        # }

        # Call LUSID to upsert our transactions
        transaction_response = cls.transaction_portfolios.upsert_transactions(
            scope=analyst_scope_code,
            code=transaction_portfolio_code,
            transactions=batch_transaction_requests)

        # Pretty print the response from LUSID
        # prettyprint.transactions_response(
        #    transaction_response,
        #    analyst_scope_code,
        #    transaction_portfolio_code)
        end = time.time()
        print('and then upsert: ' + str(end - start))




















        time2 = time3 = time4 = time5 = 0

        print('create analytic stores: ' + str(end - start))
        print('create store request: ' + str(time2))
        print('create store: ' + str(time3))
        print('append day closes : ' + str(time4))
        print('set analytics: ' + str(time5))
        print('Analytics Set')

        # now with multiple valuations at multiple dates, and multiple users, we need to send results to file
        print_file = open("output.txt", "w")

        # token timeout prevention
        token_time = datetime.now()

        # loop through the usernames and see how the aggregation varies by forSpec date range in the restrict policy
        for name, user in user_list.items():

            # we can now value the portfolio assuming different access levels and look at how the
            # stocks have been traded.

            # set up the APIs first using our user
            cls.instruments = lusid.InstrumentsApi(user)
            cls.transaction_portfolios = lusid.TransactionPortfoliosApi(user)
            cls.property_definitions = lusid.PropertyDefinitionsApi(user)
            cls.portfolios = lusid.PortfoliosApi(user)
            cls.analytic_stores = lusid.AnalyticsStoresApi(user)
            cls.aggregation = lusid.AggregationApi(user)

            # value the portfolio daily
            valuation_date = datetime(2017, 1, 1, tzinfo=pytz.utc)
            while valuation_date < termination_date:
                valuation_date += timedelta(days=1)
                if (datetime.now() - token_time).seconds > 1500:
                    # do we need to refresh token ? how do we get out the correct user to call api again?
                    token_time = datetime.now()
                # We wish to see valuations for each business date that has a close
                # and we'd also like to force valuations for 1st of the month to demonstrate the test case
                if valuation_date.day != 1:
                    # check valuation date has a close
                    format_date = datetime.strftime(valuation_date, '%b %d, %Y')
                    if format_date not in analytics_store_dates:
                        continue

                print('Valuation date is: ' + str(valuation_date))

                # Create our aggregation request
                aggregation_request = models.AggregationRequest(
                    recipe_id=models.ResourceId(
                        scope=analyst_scope_code,
                        code='default'),
                    effective_at=valuation_date,
                    metrics=[
                        models.AggregateSpec(
                            key='Holding/default/SubHoldingKey',
                            op='Value'),
                        models.AggregateSpec(
                            key='Holding/default/Units',
                            op='Sum'),
                        models.AggregateSpec(
                            key='Holding/default/Cost',
                            op='Sum'),
                        models.AggregateSpec(
                            key='Holding/default/PV',
                            op='Sum'),
                        models.AggregateSpec(
                            key='Holding/default/Price',
                            op='Sum')
                    ],
                    group_by=[
                        'Holding/default/SubHoldingKey'
                    ])
                try:
                    # Call LUSID to aggregate across all of our portfolios for 'valuation_date'
                    aggregated_portfolio = cls.aggregation.get_aggregation_by_portfolio(
                        scope=analyst_scope_code,
                        code=transaction_portfolio_code,
                        request=aggregation_request)

                except Exception as inst:
                    if inst.error.status == 403:
                        # entitlements rejects this, step to next date
                        continue
                    else:
                        raise inst

                query_params = models.TransactionQueryParameters(
                    start_date=cls.effective_date,
                    end_date=today_date,
                    query_mode='TradeDate',
                    show_cancelled_transactions=None)

                transactions_response = cls.transaction_portfolios.build_transactions(
                    scope=analyst_scope_code,
                    code=transaction_portfolio_code,
                    instrument_property_keys=['Instrument/default/Name'],
                    parameters=query_params
                )

                end = time.time()
                print('get aggregation: ' + str(end - start))
                # prettyprint.aggregation_response_paper(aggregated_portfolio)


                end = time.time()
                print('build output trans: ' + str(end - start))

                # Transactions response is a list of the trades we created
                # In each output transaction, there is a realised gain loss attribute.
                # These can be combined with position p&l to create an overall p&l.
                # Group the transactions by LUID
                output_store = {}

                for output_transaction in transactions_response.values:
                    if len(output_transaction.realised_gain_loss) > 0:      # not a ccy
                        if output_transaction.instrument_uid not in list(output_store.keys()):
                            output_store[output_transaction.instrument_uid] = {}
                        realised_gain_loss = 0
                        for item in output_transaction.realised_gain_loss:
                            realised_gain_loss += item.realised_total.amount
                        output_store[output_transaction.instrument_uid][output_transaction.transaction_date] = realised_gain_loss

                # output_store now holds all the transactions by LUID.
                # we can sum to the pv as shown earlier.

                for instrument_name, instrument_identifiers in cls.instrument_universe.items():
                    # get the trades from output_store, the end pv from aggregated_portfolio.data
                    position_pl = 0
                    trade_pl = 0
                    if instrument_identifiers['LUID'] in output_store:
                        trade_pl = sum(output_store[instrument_identifiers['LUID']].values())
                        print('trade p&l: ' + str(trade_pl))
                    for item in aggregated_portfolio.data:
                        if item['Holding/default/SubHoldingKey'] == 'LusidInstrumentId=' + instrument_identifiers['LUID'] + '/USD':
                            position_pl = item['Sum(Holding/default/PV)'] - item['Sum(Holding/default/Cost)']
                    if position_pl != 0:
                        print('pos p&l: ' + str(position_pl))

                    print('Username: ' + name + ', p&l for ' + instrument_name + ': ' + str(trade_pl + position_pl))
                    print('Username: ' + name + ', date: ' + str(valuation_date) + ' p&l for ' + instrument_name + ': ' + str(trade_pl + position_pl), file=print_file)
        print_file.close()

        # for result in aggregated_portfolio.data:
        #     if 'Currency' in result['Holding/default/SubHoldingKey']:
        #         continue
        #     sign = result['Sum(Holding/default/Units)'] / abs(result['Sum(Holding/default/Units)'])
        #     print('Instrument :' + result['Holding/default/SubHoldingKey'])
        #     print('Units :' + str(round(result['Sum(Holding/default/Units)'], 0)))
        #     print('Current Price :' + '£'  + str(
        #         round(result['Sum(Holding/default/Price)'], 2)))
        #     print(
        #           'Present Value :' + '£' + str(round(result['Sum(Holding/default/PV)'], 2)))
        #     print('Cost :' + '£' + str(round(result['Sum(Holding/default/Cost)'], 2)))
        #     print('Return :' + str(round(((result['Sum(Holding/default/PV)'] - result[
        #         'Sum(Holding/default/Cost)']) / result['Sum(Holding/default/Cost)']) * 100 * sign, 4)) + '%' + '\n')
        #
        #     total_cost += result['Sum(Holding/default/Cost)']
        #     total_pv += result['Sum(Holding/default/PV)']

        # print('TOTAL RETURN: ')
        # print((round(((total_pv - total_cost) / total_cost) * 100, 4)))
        # # create some test dates
        # dec4th17 = datetime(2017, 12, 4, tzinfo=pytz.utc)
        # dec5th17 = datetime(2017, 12, 5, tzinfo=pytz.utc)
        # dec6th17 = datetime(2017, 12, 6, tzinfo=pytz.utc)

        # tidy-up....need to delete policies and roles for re-running
        #response = cls.shrine_client.api_roles_by_code_delete(role_code_allow)
        #response = cls.shrine_client.api_roles_by_code_delete(role_code_restrict)
        #response = cls.shrine_client.api_policies_by_code_delete(policy_code_restrict)
        #response = cls.shrine_client.api_policies_by_code_delete(policy_code_allow)

    @classmethod
    def tearDownClass(cls):
        for name, item in cls.instrument_universe.items():
            response = cls.instruments.delete_instrument(InstrumentLoader.FIGI_SCHEME, item['Figi'])
    @classmethod
    def load_instruments_from_file(cls):
        inst_list = pd.read_csv(cls.INSTRUMENT_FILE)
        return inst_list
    @classmethod
    def load_transactions_from_file(cls, csv_file):
        csv_transactions = cls.import_csv_file(csv_file)
        transactions = {}

        for index, transaction in csv_transactions.iterrows():
            transactions[transaction['transaction_id']] = {
                'type': transaction['transaction_type'],
                'portfolio': transaction['portfolio_name'],
                'instrument_name': transaction['instrument_name'],
                'instrument_uid': cls.instrument_universe[transaction['instrument_name']]['Figi'],
                'transaction_date': parser.parse(transaction['transaction_date']).replace(tzinfo=pytz.utc),
                'settlement_date': (parser.parse(transaction['transaction_date']) + timedelta(days=2)).replace(tzinfo=pytz.utc),
                'units': transaction['transaction_units'],
                'transaction_price': transaction['transaction_price'],
                'transaction_currency': transaction['transaction_currency'],
                'total_cost': transaction['transaction_cost'],
                'strategy': transaction['transaction_strategy']}
            # print(index)
        return transactions

    @classmethod
    def import_csv_file(cls, csv_file):
        """
        This function is used to import data form our csv files
        """
        data = pd.read_csv(csv_file)
        return data

    @classmethod
    def import_json_file(cls, json_file):
        """
        This function is used to import data form our json files
        """
        with open(os.path.join('./data/', json_file), "r") as openfile:
            data = json.load(openfile)
        return data

    @classmethod
    def create_shrine_lusid_clients(cls, username, password, client_id, client_secret, token_url):
        # Prepare our authentication request
        token_request_body = ("grant_type=password&username={0}".format(username) +
                              "&password={0}&scope=openid client groups".format(password) +
                              "&client_id={0}&client_secret={1}".format(client_id, client_secret))
        headers = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}

        # Make our authentication request
        okta_response = requests.post(token_url, data=token_request_body, headers=headers)

        # Ensure that we have a 200 response code
        assert okta_response.status_code == 200

        # Retrieve our api token from the authentication response
        cls.api_token = {"access_token": okta_response.json()["access_token"]}

        # Initialise our API client using our token so that we can include it in all future requests
        credentials = BasicTokenAuthentication(cls.api_token)

        cls.client = lusid.LUSIDAPI(credentials, cls.api_url)
        # Do the same for Shrine - note the call is slightly different for now, with the token being passed in later
        shrine_url = 'https://shrine-am-ci.lusid.com'
        cls.shrine_client = shrine.FINBOURNEShrineAPI(shrine_url)
        return credentials
    @classmethod
    def upsert_intruments(cls, inst_list):
        # Initialise our batch upsert request
        batch_upsert_request = {}
        # Iterate over our instrument universe
        for row in inst_list.iterrows():
            # Collect our instrument, note that row[0] gives you the index
            instrument = row[1]
            instrument_ticker = models.InstrumentProperty(cls.TICKER_PROPERTY_KEY,  models.PropertyValue(instrument['instrument_name']))

            # Add the instrument to our batch request using the FIGI as the main unique identifier
            batch_upsert_request[instrument['instrument_name']] = models.InstrumentDefinition(
                name=instrument['instrument_name'],
                identifiers={cls.FIGI_SCHEME: models.InstrumentIdValue(instrument['figi'])},
                properties=[instrument_ticker])


        # Call LUSID to upsert our batch
        instrument_response = cls.instruments.upsert_instruments(requests=batch_upsert_request)

        # Pretty print the response from LUSID
        # prettyprint.instrument_response(instrument_response, identifier='Figi')
        identifier = 'Figi'
        for instrument_name, instrument in instrument_response.values.items():

            # Build a global dictionary of name-figi pairs for use throughout the use-case
            cls.instrument_universe[instrument_name]={}
            cls.instrument_universe[instrument_name]['Figi'] = instrument.identifiers['Figi']
            cls.instrument_universe[instrument_name]['LUID'] = instrument.lusid_instrument_id
            # print results
            print('Instrument Successfully Upserted: ' + instrument_name)
            print(instrument.identifiers[identifier])
            print('LUSID Instrument ID: ' + instrument.lusid_instrument_id)
            print('\n')

        print(len(instrument_response.values), ' instruments upserted successfully')
        print(len(instrument_response.failed), ' instrument upsert failures')

    @classmethod
    def api_populate_path_values(cls):
        # Shrine paths to apply the policy to
        path_values = [
            "api-datatypes-getdatatype",
            "api-aggregation-getaggregationbyportfolio",
            "api-datatypes-getunitsfromdatatype",
            "api-datatypes-listdatatypes",
            "api-derivedtransactionportfolios-createderivedportfolio",
            "api-health-verify"
            "api-instruments-getinstrument",
            "api-instruments-getinstrumentidentifiers",
            "api-instruments-getinstruments",
            "api-instruments-listinstruments",
            "api-portfoliogroups-createportfoliogroup",
            "api-portfoliogroups-deleteportfoliofromgroup",
            "api-portfoliogroups-deleteportfoliogroup",
            "api-portfoliogroups-deletesubgroupfromgroup",
            "api-portfoliogroups-getportfoliogroup",
            "api-portfoliogroups-getportfoliogroupcommands",
            "api-portfoliogroups-getportfoliogroupexpansion",
            "api-portfoliogroups-listportfoliogroups",
            "api-portfoliogroups-updateportfoliogroup",
            "api-portfolios-deleteportfolio",
            "api-portfolios-deleteportfolioproperties",
            "api-portfolios-getportfolio",
            "api-portfolios-getportfoliocommands",
            "api-portfolios-getportfolioproperties",
            "api-portfolios-listportfolios",
            "api-portfolios-listportfoliosforscope",
            "api-portfolios-updateportfolio",
            "api-portfolios-upsertportfolioproperties",
            "api-propertydefinitions-createpropertydefinition",
            "api-propertydefinitions-getmultiplepropertydefinitions",
            "api-propertydefinitions-getpropertydefinition",
            "api-propertydefinitions-updatepropertydefinition",
            "api-reconciliation-reconcileholdings",
            "api-reconciliation-reconcilevaluation",
            "api-referenceportfolios-listconstituentsadjustments",
            "api-referenceportfolios-upsertreferenceportfolioconstituents",
            "api-schemas-getentityschema",
            "api-schemas-getpropertyschema",
            "api-schemas-getvaluetypes",
            "api-scopes-listscopes",
            "api-searchproxy-instrumentssearch",
            "api-searchproxy-portfoliogroupssearch",
            "api-searchproxy-portfoliossearch",
            "api-searchproxy-propertiessearch",
            "api-transactionportfolios-addtransactionproperty",
            "api-transactionportfolios-adjustholdings",
            "api-transactionportfolios-buildtransactions",
            "api-transactionportfolios-canceladjustholdings",
            "api-transactionportfolios-createportfolio",
            "api-transactionportfolios-deleteexecutions",
            "api-transactionportfolios-deletepropertyfromtransaction",
            "api-transactionportfolios-deletetransactions",
            "api-transactionportfolios-getdetails",
            "api-transactionportfolios-getholdings",
            "api-transactionportfolios-getholdingsadjustment",
            "api-transactionportfolios-gettransactions",
            "api-transactionportfolios-listholdingsadjustments",
            "api-transactionportfolios-setholdings",
            "api-transactionportfolios-upsertexecutions",
            "api-transactionportfolios-upsertportfoliodetails",
            "api-transactionportfolios-upserttransactions"
        ]
        return path_values

    def test_run_aggregation_with_buy(self):

        print("here")

    def run_aggregation(self, tran_requests):

        print("here")


if __name__ == '__main__':
    unittest.main()
