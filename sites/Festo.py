import pandas as pd

class Festo:
  # import the FESTO SVHC / Exemption list
  substances = pd.read_csv('./sites/FESTO SCIP Notifications Status_vers. g_28.10.2022 - rearranged.csv', dtype=str)

  def multiple_results(results, search_term):
    """
    If more than one result is found, search for the exact match in Festo Part Number or Festo Order Code
    """
    # loop through all products in the search result
    for product in results['products']:
      # check whether Festo Part Number or Festo Order Code exactly matches with the search term
      if str(product['code']) == str(search_term) or str(product['orderCode']) == str(search_term):
        # if exact match is found, return the match
        return product

    # if no exact match is found, return error message
    print(f'part number {search_term} is not found on server')
    return {"status":404}

if __name__ == "__main__":
  print(Festo().substances.loc[Festo().substances['Identifier'] == str(8046265)])