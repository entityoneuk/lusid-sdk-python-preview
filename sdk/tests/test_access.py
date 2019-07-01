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
        # with open(os.path.join(dir_path, "secrets.json"), "r") as secrets:
        #     config = json.load(secrets)
        #
        # token_url = os.getenv("FBN_TOKEN_URL", config["api"]["tokenUrl"])
        # 3 users - restricted, admin and super

        # username_super = os.getenv("FBN_USERNAME", config["api"]["username_super"])
        # username_admin = os.getenv("FBN_USERNAME", config["api"]["username_admin"])
        # username_restricted = os.getenv("FBN_USERNAME", config["api"]["username_restricted"])
        #
        # password_super = pathname2url(os.getenv("FBN_PASSWORD", config["api"]["password_super"]))
        # password_admin = pathname2url(os.getenv("FBN_PASSWORD", config["api"]["password_admin"]))
        # password_restricted = pathname2url(os.getenv("FBN_PASSWORD", config["api"]["password_restricted"]))
        #
        # client_id = pathname2url(os.getenv("FBN_CLIENT_ID", config["api"]["clientId"]))
        # client_secret = pathname2url(os.getenv("FBN_CLIENT_SECRET", config["api"]["clientSecret"]))
        #

        # create multiple configured API clients
        cls.client_restricted = ApiClientBuilder().build("secrets-restricted.json")
        cls.client_admin = ApiClientBuilder().build("secrets-admin.json")

        cls.client_super = ApiClientBuilder().build("secrets-super.json")




        user_list = {"administrator": cls.client_admin, "restricted": cls.client_restricted}

        # set up the APIs
        cls.instruments = lusid.InstrumentsApi(cls.client_super)
        cls.transaction_portfolios = lusid.TransactionPortfoliosApi(cls.client_super)
        cls.property_definitions = lusid.PropertyDefinitionsApi(cls.client_super)
        cls.portfolios = lusid.PortfoliosApi(cls.client_super)
        cls.analytic_stores = lusid.AnalyticsStoresApi(cls.client_super)
        cls.aggregation = lusid.AggregationApi(cls.client_super)


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
        scope = "finbourne"
        analyst_scope_code = 'notepad-access-' + scope          # + "-" + str(uuid_gen)

        ################
        # Cut-down or full sized test?
        # Full-sized test runs from 1/1/17 to 31/12/18 (2 full years)
        # Short from 1/1/17 to 31/3/17 (3 months)
        cutdown = True
        if cutdown:
            close_file = 'data/company_closing_prices_no_divis_short.csv'
            transactions_file = 'data/DJIItransactions_short.csv'
            cls.INSTRUMENT_FILE = 'data/DOW Figis_short.csv'
            transaction_portfolio_code = 'DJII_30s'
            termination_date = datetime(2017, 4, 4, tzinfo=pytz.utc)
        else:
            close_file = 'data/company_closing_prices_no_divis_matched.csv'
            transactions_file = 'data/DJIItransactions.csv'
            cls.INSTRUMENT_FILE = 'data/DOW Figis.csv'
            transaction_portfolio_code = 'DJII_30f'
            termination_date = datetime(2018, 12, 31, tzinfo=pytz.utc)

        today_date = datetime(2018, 12, 31, tzinfo=pytz.utc)

        ##################################
        # Create policies with access, timing etc (really show off shrine capabilities)
        # Create roles with groups of these policies
        # In Okta, create accounts. Attached roles to these accounts
        # 1 We first create policies, which describe the permissions (e.g r access to LUSID, r-w to SHRINE)
        # 2 We create roles, which are collections of policies
        # 3 OKTA has been manually updated to create two users, cleric01 and manager01 and two groups
        # The secrets file contains login

        # Name the policies and roles
        policy_code_allow = "ViewPolicyAllow"
        policy_code_restricted = "ViewPolicyRestricted"
        policy_code_restricted1 = "ViewPolicyRestricted1"
        role_code_restrict = "clerical-limited-access"
        role_code_allow = "manager-all-access"

        # first delete policies if they exist
        # delete the policy if it exists
        def try_delete_resource(f):
            try:
                f()
            except Exception as ex:
                error = ex.message
                print("WARNING: " + error)

        try_delete_resource(lambda: cls.shrine_client.api_policies_by_code_delete(policy_code_restricted))
        try_delete_resource(lambda: cls.shrine_client.api_policies_by_code_delete(policy_code_restricted1))
        try_delete_resource(lambda: cls.shrine_client.api_policies_by_code_delete(policy_code_allow))
        try_delete_resource(lambda: cls.shrine_client.api_roles_by_code_delete(role_code_allow))
        try_delete_resource(lambda: cls.shrine_client.api_roles_by_code_delete(role_code_restrict))

        # Create a policy

        policy_activate_date = datetime(2016, 1, 1, tzinfo=pytz.utc)
        policy_deactivate_date = datetime(2020, 1, 1, tzinfo=pytz.utc)

        policy_from_date = datetime(2017, 1, 1, tzinfo=pytz.utc)
        policy_to_date = datetime(2018, 1, 1, tzinfo=pytz.utc)

        model_when_spec = shrine_models.WhenSpec()
        model_when_spec.activate = policy_activate_date
        model_when_spec.deactivate = policy_deactivate_date
        model_for_spec = shrine_models.ForSpec()
        effective_range = shrine_models.EffectiveRange(from_property=policy_from_date, to=policy_to_date)
        #effective_relative = shrine_models.EffectiveRange(from_property=policy_from_date, to=policy_to_date)
        effective_quality = shrine_models.EffectiveDateHasQuality(quality="IsFirstDayOfAnyMonth")
        #model_for_spec.effective_range = effective_range
        model_for_spec.effective_date_has_quality = effective_quality
        #model_for_spec.effective_date_relative = effective_relative
        action_portfolio = shrine_models.ActionId(scope="default", activity="Any", entity="Portfolio")
        action_datatype_read = shrine_models.ActionId(scope="default", activity="Read", entity="DataType")
        action_propertydef_add = shrine_models.ActionId(scope="default", activity="Add", entity="PropertyDefinition")
        action_propertydef_read = shrine_models.ActionId(scope="default", activity="Read", entity="PropertyDefinition")

        # Here we connect the policy to the portfolio via the scope code.
        scope_id_path_def = shrine_models.ScopeIdPathDefinition(
            scope=analyst_scope_code
        )
        id_path_def = shrine_models.IdPathDefinition(
            scope_id_path_definition=scope_id_path_def,
            category="Identifier",
            actions=[action_portfolio, action_propertydef_add, action_propertydef_read],
            name="Notepad-view",
            description="View notepad"
        )

        scope_and_code_idp2 = shrine_models.ScopeAndCodeIdPathDefinition("default", "string")
        id_path_def2 = shrine_models.IdPathDefinition(
            scope_and_code_id_path_definition=scope_and_code_idp2,
            category="Identifier",
            actions=[action_datatype_read],
            name="Notepad-view",
            description="View notepad"
        )

        scope_id_path_def3 = shrine_models.ScopeIdPathDefinition(
            scope="default"
        )
        id_path_def3 = shrine_models.IdPathDefinition(
            scope_id_path_definition=scope_id_path_def3,
            category="Identifier",
            actions=[action_propertydef_read],
            name="Notepad-view",
            description="View notepad"
        )

        scope_and_code_idp4 = shrine_models.ScopeAndCodeIdPathDefinition("default", "*")
        id_path_def4 = shrine_models.IdPathDefinition(
            scope_and_code_id_path_definition=scope_and_code_idp4,
            category="Identifier",
            actions=[action_datatype_read],
            name="Notepad-view",
            description="View notepad"
        )
        # need a further path for the 'restrict' 'portfolio' policy
        id_path_def5 = shrine_models.IdPathDefinition(
            scope_id_path_definition=scope_id_path_def,
            category="Identifier",
            actions=[action_portfolio],
            name="Notepad-view",
            description="View notepad"
        )

        path_view = shrine_models.PathDefinition(id_path_definition=id_path_def)
        path_view2 = shrine_models.PathDefinition(id_path_definition=id_path_def2)
        path_view3 = shrine_models.PathDefinition(id_path_definition=id_path_def3)
        path_view4 = shrine_models.PathDefinition(id_path_definition=id_path_def4)
        path_view5 = shrine_models.PathDefinition(id_path_definition=id_path_def5)

        # Last path definition is for the LUSID library of API calls, this is necessary for valuation later
        path_values = cls.api_populate_path_values()
        api_path_definitions = [shrine_models.PathDefinition(id_path_definition=shrine_models.IdPathDefinition(
            scope_and_code_id_path_definition=shrine_models.ScopeAndCodeIdPathDefinition(
                scope="LUSID",
                code=path),
            category="Identifier",
            actions=[shrine_models.ActionId(scope="LUSID", activity="Execute", entity="Feature")],
            name=path,
            description=path))
            for path in path_values]

        # Create the policies designed to grant and restrict access to LUSID data within our scope
        policy_allow = shrine_models.PolicyCreationRequest(
            code=policy_code_allow,
            description='Policy to allow viewing of notepad portfolio',
            applications=['Lusid'],
            grant='ALLOW',
            paths=[path_view, path_view2, path_view3, path_view4] + api_path_definitions,
            when=model_when_spec
        )
        policy_restrict = shrine_models.PolicyCreationRequest(
            code=policy_code_restricted,
            description='Policy to restrict viewing of notepad portfolio',
            applications=['Lusid'],
            grant="ALLOW",
            paths=[path_view2, path_view3, path_view4] + api_path_definitions,
            when=model_when_spec
        )
        # additional restrict policy for the use case
        # important...! only attach the forspec to this portfolio access policy
        # otherwise the other actions will be tested against this criteria
        policy_restrict1 = shrine_models.PolicyCreationRequest(
            code=policy_code_restricted1,
            description='Policy to restrict viewing of notepad portfolio',
            applications=['Lusid'],
            grant="ALLOW",
            paths=[path_view5],
            when=model_when_spec,
            for_property=[model_for_spec]
        )

        # # finally, we need a policy to allow access to the api. this is the same for both accounts
        # allow_portfolios_policy_request = shrine_models.PolicyCreationRequest(
        #     code=policy_code_api_execute,
        #     description="Allows access to API end points",
        #     applications=['Lusid'],
        #     grant="Allow",
        #     paths=path_definitions,
        #     when=model_when_spec
        # )

        # tokenid = cls.client_super.configuration.credentials.token
        # custom_header = {'Authorization': 'Bearer ' + tokenid}

        # check before submitting that you are not duplicating policies, this is not permitted
        try:
            response = cls.shrine_client.api_policies_by_code_get(policy_code_allow)
        except Exception as inst:
            if inst.error.response.status_code == 404:
                # Policy does not exist, create.
                response = cls.shrine_client.api_policies_post(policy_allow)
        try:
            response = cls.shrine_client.api_policies_by_code_get(policy_code_restricted)
        except Exception as inst:
            if inst.error.response.status_code == 404:
                # Policy does not exist, create.
                response = cls.shrine_client.api_policies_post(policy_restrict)
        try:
            response = cls.shrine_client.api_policies_by_code_get(policy_code_restricted1)
        except Exception as inst:
            if inst.error.response.status_code == 404:
                # Policy does not exist, create.
                response = cls.shrine_client.api_policies_post(policy_restrict1)
        # create a role for someone not allowed to view transactions - clerical level access
        # and someone allowed full access - manager level

        policyID_cleric = shrine_models.PolicyId(scope="default", code=policy_code_restricted)
        policyID_cleric1 = shrine_models.PolicyId(scope="default", code=policy_code_restricted1)
        policyID_manager = shrine_models.PolicyId(scope="default", code=policy_code_allow)

        policyIDresource_cleric = shrine_models.PolicyIdRoleResource(
            policy_identifiers=[policyID_cleric, policyID_cleric1],
            policy_collection_identifiers=[]
        )

        policyIDresource_manager = shrine_models.PolicyIdRoleResource(
            policy_identifiers=[policyID_manager],
            policy_collection_identifiers=[]
        )
        resource_cleric = shrine_models.RoleResourceRequest(policy_id_role_resource=policyIDresource_cleric)
        resource_manager = shrine_models.RoleResourceRequest(policy_id_role_resource=policyIDresource_manager)

        role_cleric = shrine_models.RoleCreationRequest(
            code=role_code_restrict,
            description="Test role for lesser access",
            resource=resource_cleric,
            when=model_when_spec
        )

        role_manager = shrine_models.RoleCreationRequest(
            code=role_code_allow,
            description="Test role for all access",
            resource=resource_manager,
            when=model_when_spec
        )

        # check before submitting that you are not duplicating roles, this is not permitted

        try:
            response = cls.shrine_client.api_roles_by_code_get(role_code_restrict)
        except Exception as inst:
            if inst.error.response.status_code == 404:
                # Role does not exist, create
                response = cls.shrine_client.api_roles_post(role_cleric)

        try:
            response = cls.shrine_client.api_roles_by_code_get(role_code_allow)
        except Exception as inst:
            if inst.error.response.status_code == 404:
                # Role does not exist, create
                response = cls.shrine_client.api_roles_post(role_manager)


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

        # Create the request to add our portfolio
        transaction_portfolio_request = models.CreateTransactionPortfolioRequest(
            display_name=transaction_portfolio_code,
            code=transaction_portfolio_code,
            base_currency='USD',
            description='Paper transaction portfolio',
            created=portfolio_creation_date)

        # Call LUSID to create our portfolio
        try:
            response = cls.portfolios.get_portfolio(scope=analyst_scope_code, code=transaction_portfolio_code)
        except Exception as err_response:
            if err_response.status == 404:
                # portfolio does not exist, create.
                response = cls.transaction_portfolios.create_portfolio(scope=analyst_scope_code, create_request=transaction_portfolio_request)

        # Pretty print the response from LUSID
        # prettyprint.portfolio_response(portfolio_response)

        ##################################
        # Populating our analyst's portfolio with a starting cash balance

        # Set the date from which the cash balance will apply to be just after portfolio creation
        holdings_effective_date = cls.effective_date

        # Define our initial cash balance
        initial_cash_balance = 30000000     # $30mil, so 1mil per line?

        # Create a holding adjustment to set our initial cash balance
        holding_adjustment = [
            models.AdjustHoldingRequest(
                instrument_identifiers={'Instrument/default/Currency': 'USD'},
                tax_lots=[
                    models.TargetTaxLotRequest(
                        units=initial_cash_balance,
                        cost=models.CurrencyAndAmount(
                            amount=initial_cash_balance,
                            currency='USD'),
                        portfolio_cost=initial_cash_balance,
                        price=1)
                ]
            )
        ]

        # Call LUSID to set our initial cash balance
        set_holdings_response = cls.transaction_portfolios.set_holdings(
            scope=analyst_scope_code,
            code=transaction_portfolio_code,
            effective_at=holdings_effective_date,
            holding_adjustments=holding_adjustment)

        # Pretty print our response from LUSID
        #prettyprint.set_holdings_response(
        #    set_holdings_response,
        #    analyst_scope_code,
        #    transaction_portfolio_code)
        end = time.time()

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
                scope='system',
                code='string')
            )

        # Call LUSID to create our property
        #cls.property_definitions.delete_property_definition(domain='Trade', scope=analyst_scope_code, code='strategy')
        try:
            property_response = cls.property_definitions.get_property_definition(domain='Trade', scope=analyst_scope_code, code='strategy')
        except Exception as err_response:
            if err_response.status == 404:       #why is this different
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
        instrument_analytics = {}

        for row in instrument_close_prices.iterrows():
            # group closing prices by date for analytics store

            instrument = row[1]

            if 'Cash' in instrument['Name']:
                continue

            # Get our Lusid Instrument Id

            luid = cls.instrument_universe[instrument['Name']]['LUID']
            # check the date to see if anything stands against it yet. If it's new, add a list item (for a new store)
            if instrument['Date'] not in analytics_store_dates:
                analytics_store_dates.append(instrument['Date'])
                instrument_analytics[instrument['Date']] = {}

            # add price/instrument to existing store
            instrument_analytics[instrument['Date']][instrument['Name']] = models.InstrumentAnalytic(
                instrument_uid=luid,
                value=instrument['AdjClose'])
        end = time.time()
        print('close prices by date: ' + str(end - start))

        time2 = time3 = time4 = time5 = 0
        for date, date_item in instrument_analytics.items():
            # Create analytics store request - one required for each date there are prices
            point1 = time.time()
            format_date =parser.parse(date).replace(tzinfo=pytz.utc)
            year = format_date.year
            month = format_date.month
            day = format_date.day

            analytics_store_request = models.CreateAnalyticStoreRequest(scope=analyst_scope_code,
                                                                        date=format_date)
            point2 = time.time()
            time2 += (point2 - point1)

            try:
                store_response = cls.analytic_stores.get_analytic_store(scope=analyst_scope_code, year=year, month=month, day=day)
            except Exception as err_response:
                if err_response.status == 404:
                    # store does not exist, create.
                    # Call LUSID to create our analytics store
                    cls.analytic_stores.create_analytic_store(request=analytics_store_request)

            point3 = time.time()
            time3 += (point3 - point2)
            days_closes = []
            for inst_name, instrument_analytic_item in date_item.items():
                days_closes.append(instrument_analytic_item)
            point4 = time.time()
            time4 += (point4 - point3)
            # Call LUSID to set up our newly created analytics store with our prices
            cls.analytic_stores.set_analytics(scope=analyst_scope_code,
                                     year=year,
                                     month=month,
                                     day=day,
                                     data=days_closes)
            point5 = time.time()
            time5 += (point5 - point4)
        end = time.time()
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
                # if (datetime.now() - token_time).seconds > 1500:
                #     # do we need to refresh token ? how do we get out the correct user to call api again?
                #     token_time = datetime.now()
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
                    if inst.status == 403:
                        # entitlements rejects this, step to next date
                        continue
                    else:
                        raise inst

                query_params = models.TransactionQueryParameters(
                    start_date=cls.effective_date,
                    end_date=valuation_date,
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
            # response = cls.client_super.instruments.delete_instrument(InstrumentLoader.FIGI_SCHEME, item['Figi'])
            print("teardown")
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
