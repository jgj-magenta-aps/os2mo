import { Selector } from 'testcafe'
import { baseURL } from './support'
import VueSelector from 'testcafe-vue-selectors'

let moment = require('moment')

fixture('Organisation test')
  .page(`${baseURL}/organisation`)

const dialog = Selector('#orgUnitRename')

const parentInput = dialog.find('input[data-vv-as="Enhed"]')

const fromInput = dialog.find('.from-date input.form-control')

test('Workflow: rename unit', async t => {
  let today = moment()

  await t

    .hover('#mo-workflow', {offsetX: 10, offsetY: 50})
    .expect(Selector('.btn-unit-rename').visible).ok()
    .click('.btn-unit-rename')

    .expect(dialog.exists).ok('Opened dialog')

    .click(parentInput)
    .click(dialog.find('li .item .link-color'))

    .typeText(dialog.find('input[data-vv-as="Nyt navn"]'), 'Ballerup Hovedbibliotek')

    .click(fromInput)
    .hover(dialog.find('.vdp-datepicker .day:not(.blank)')
           .withText(today.date().toString()))
    .click(dialog.find('.vdp-datepicker .day:not(.blank)')
           .withText(today.date().toString()))
    .expect(fromInput.value).eql(today.format('DD-MM-YYYY'))

    .click(dialog.find('.btn-primary'))

    .expect(dialog.exists).notOk()

    .expect(VueSelector('MoLog MoWorklog')
            .find('.alert').nth(-1).innerText)
    .match(
      /Organisationsenheden med UUID [-0-9a-f]* er blevet omdøbt/
    )
})
